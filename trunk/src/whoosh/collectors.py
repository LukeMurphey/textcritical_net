# Copyright 2012 Matt Chaput. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY MATT CHAPUT ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL MATT CHAPUT OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Matt Chaput.

"""
This module contains "collector" objects. Collectors provide a way to gather
"raw" results from a :class:`whoosh.matching.Matcher` object, implement
sorting, filtering, collation, etc., and produce a
:class:`whoosh.searching.Results` object.

The basic collectors are:

TopCollector
    Returns the top N matching results sorted by score, using block-quality
    optimizations to skip blocks of documents that can't contribute to the top
    N. The :meth:`whoosh.searching.Searcher.search` method uses this type of
    collector by default or when you specify a ``limit``.

UnlimitedCollector
    Returns all matching results sorted by score. The
    :meth:`whoosh.searching.Searcher.search` method uses this type of collector
    when you specify ``limit=None`` or you specify a limit equal to or greater
    than the number of documents in the searcher.

SortingCollector
    Returns all matching results sorted by a :class:`whoosh.sorting.Facet`
    object. The :meth:`whoosh.searching.Searcher.search` method uses this type
    of collector when you use the ``sortedby`` parameter.

Here's an example of a simple collector that instead of remembering the matched
documents just counts up the number of matches::

    class CountingCollector(Collector):
        def prepare(self, top_searcher, q, requires_matcher=False):
            # Always call super method in prepare
            Collector.prepare(self, top_searcher, q, requires_matcher)
            
            self.count = 0
        
        def collect(self, sub_docnum):
            self.count += 1
    
    c = CountingCollector()
    mysearcher.search_with_collector(myquery, c)
    print(c.count)

There are also several wrapping collectors that extend or modify the
functionality of other collectors. The meth:`whoosh.searching.Searcher.search`
method uses many of these when you specify various parameters.

NOTE: collectors are not designed to be reentrant or thread-safe. It is
generally a good idea to create a new collector for each search.
"""

import threading
from array import array
from bisect import insort
from collections import defaultdict
from heapq import heapify, heappush, heapreplace

from whoosh import sorting
from whoosh.compat import abstractmethod, iteritems, itervalues, xrange
from whoosh.searching import Hit, Results, TimeLimit
from whoosh.util import now


# Base class

class Collector(object):
    """Base class for collectors.
    """

    def prepare(self, top_searcher, q, requires_matcher=False):
        """This method is called before a search.
        
        Subclasses can override this to perform set-up work, but
        they should still call the superclass's method because it sets several
        necessary attributes on the collector object:
        
        self.top_searcher
            The top-level searcher.
        self.q
            The query object
        self.requires_matcher
            Whether a wrapping collector requires that this collector's matcher
            be in a valid state at every call to ``collect()``. If this is
            ``False``, the collector is free to use faster methods that don't
            necessarily keep the matcher updated, such as
            ``matcher.all_ids()``.
        
        :param top_searcher: the top-level :class:`whoosh.searching.Searcher`
            object.
        :param q: the :class:`whoosh.query.Query` object being searched for.
        :param requires_matcher: whether a wrapping collector needs this
            collector to step through the matches individually.
        """

        self.top_searcher = top_searcher
        self.q = q
        self.requires_matcher = requires_matcher

        self.runtime = None
        self.starttime = now()
        self.docset = set()

    def set_subsearcher(self, subsearcher, offset):
        """This method is called each time the collector starts on a new
        sub-searcher.
        
        Subclasses can override this to perform set-up work, but
        they should still call the superclass's method because it sets several
        necessary attributes on the collector object:
        
        self.subsearcher
            The current sub-searcher. If the top-level searcher is atomic, this
            is the same as the top-level searcher.
        self.offset
            The document number offset of the current searcher. You must add
            this number to the document number passed to
            :meth:`Collector.collect` to get the top-level document number
            for use in results.
        self.matcher
            A :class:`whoosh.matching.Matcher` object representing the matches
            for the query in the current sub-searcher.
        """

        self.subsearcher = subsearcher
        self.offset = offset
        self.matcher = self.q.matcher(subsearcher)

    def collect_matches(self):
        """This method calls :meth:`Collector.matches` and then for each
        matched document calls :meth:`Collector.collect`. Sub-classes that
        want to intervene between finding matches and adding them to the
        collection (for example, to filter out certain documents) can override
        this method.
        """

        collect = self.collect
        for sub_docnum in self.matches():
            collect(sub_docnum)

    @abstractmethod
    def collect(self, sub_docnum):
        """This method is called for every matched document. It should do the
        work of adding a matched document to the results, and it should return
        an object to use as a "sorting key" for the given document (such as the
        document's score, a key generated by a facet, or just None). Subclasses
        must implement this method.
        
        If you want the score for the current document, use
        ``self.matcher.score()``.
        
        Overriding methods should add the current document offset
        (``self.offset``) to the ``sub_docnum`` to get the top-level document
        number for the matching document to add to results.
        
        :param sub_docnum: the document number of the current match within the
            current sub-searcher. You must add ``self.offset`` to this number
            to get the document's top-level document number.
        """

        raise NotImplementedError

    @abstractmethod
    def sort_key(self, sub_docnum):
        """Returns a sorting key for the current match. This should return the
        same value returned by :meth:`Collector.collect`, but without the side
        effect of adding the current document to the results.

        If the collector has been prepared with ``requires_matcher=True``,
        this method can use ``self.matcher`` to get information, for example
        the score. Otherwise, it should only use the provided ``sub_docnum``,
        since the matcher may be in an inconsistent state.
        
        Subclasses must implement this method.
        """

        raise NotImplementedError

    def remove(self, global_docnum):
        """Removes a document from the collector. Not that this method uses the
        global document number as opposed to :meth:`Collector.collect` which
        takes a segment-relative docnum.
        """

        items = self.items
        for i in xrange(len(items)):
            if items[i][1] == global_docnum:
                items.pop(i)
                return
        raise KeyError(global_docnum)

    def _step_through_matches(self):
        matcher = self.matcher
        while matcher.is_active():
            yield matcher.id()
            matcher.next()

    def matches(self):
        """Yields a series of relative document numbers for matches
        in the current subsearcher.
        """

        # We jump through a lot of hoops to avoid stepping through the matcher
        # "manually" if we can because all_ids() is MUCH faster
        if self.requires_matcher:
            return self._step_through_matches()
        else:
            return self.matcher.all_ids()

    def finish(self):
        """This method is called after a search.
        
        Subclasses can override this to perform set-up work, but
        they should still call the superclass's method because it sets several
        necessary attributes on the collector object:
        
        self.runtime
            The time (in seconds) the search took.
        """

        self.runtime = now() - self.starttime

    def _results(self, items, **kwargs):
        # Fills in a Results object with the invariant information and the
        # given "items" (a list of (score, docnum) tuples)
        return Results(self.top_searcher, self.q, items, runtime=self.runtime,
                       **kwargs)

    @abstractmethod
    def results(self):
        """Returns a :class:`~whoosh.searching.Results` object containing the
        results of the search. Subclasses must implement this method
        """

        raise NotImplementedError


# Scored collectors

class ScoredCollector(Collector):
    """Base class for collectors that sort the results based on document score.
    """

    def __init__(self, replace=10, **kwargs):
        """
        :param replace: Number of matches between attempts to replace the
            matcher with a more efficient version.
        """

        Collector.__init__(self, **kwargs)
        self.replace = replace

    def prepare(self, top_searcher, q, requires_matcher=False):
        # This collector requires a valid matcher at each step
        Collector.prepare(self, top_searcher, q, True)

        if top_searcher.weighting.use_final:
            self.final_fn = top_searcher.weighting.final
        else:
            self.final_fn = None

        # Heap containing top N (score, 0-docnum) pairs
        self.items = []
        # Minimum score a document must have to make it into the top N. This is
        # used by the block-quality optimizations
        self.minscore = 0
        # Number of times the matcher was replaced (for debugging)
        self.replaced_times = 0
        # Number of blocks skipped by quality optimizations (for debugging)
        self.skipped_times = 0

    def sort_key(self, sub_docnum):
        return 0 - self.matcher.score()

    def collect(self, sub_docnum):
        # Do common work to calculate score and top-level document number
        global_docnum = self.offset + sub_docnum

        score = self.matcher.score()
        if self.final_fn:
            score = self.final_fn(self.top_searcher, global_docnum, score)

        # Call specialized method on subclass
        return self._collect(global_docnum, score)

    def matches(self):
        minscore = self.minscore
        matcher = self.matcher
        usequality = self._use_block_quality()
        replace = self.replace
        replacecounter = 0

        # A flag to indicate whether we should check block quality at the start
        # of the next loop
        checkquality = True

        while matcher.is_active():
            # If the replacement counter has reached 0, try replacing the
            # matcher with a more efficient version
            if replace:
                if replacecounter == 0 or self.minscore != minscore:
                    self.matcher = matcher = matcher.replace(minscore or 0)
                    self.replaced_times += 1
                    if not matcher.is_active():
                        break
                    usequality = self._use_block_quality()
                    replacecounter = self.replace
                    minscore = self.minscore
                replacecounter -= 1

            # If we're using block quality optimizations, and the checkquality
            # flag is true, try to skip ahead to the next block with the
            # minimum required quality
            if usequality and checkquality and minscore is not None:
                self.skipped_times += matcher.skip_to_quality(minscore)
                # Skipping ahead might have moved the matcher to the end of the
                # posting list
                if not matcher.is_active():
                    break

            yield matcher.id()

            # Move to the next document. This method returns True if the
            # matcher has entered a new block, so we should check block quality
            # again.
            checkquality = matcher.next()


class TopCollector(ScoredCollector):
    """A collector that only returns the top "N" scored results.
    """

    def __init__(self, limit=10, usequality=True, **kwargs):
        """
        :param limit: the maximum number of results to return.
        :param usequality: whether to use block-quality optimizations. This may
            be useful for debugging.
        """

        ScoredCollector.__init__(self, **kwargs)
        self.limit = limit
        self.usequality = usequality

    def _use_block_quality(self):
        return (self.usequality
                and not self.top_searcher.weighting.use_final
                and self.matcher.supports_block_quality())

    # ScoredCollector.collect calls this
    def _collect(self, global_docnum, score):
        items = self.items

        # Document numbers are negated before putting them in the heap so that
        # higher document numbers have lower "priority" in the queue. Lower
        # document numbers should always come before higher document numbers
        # with the same score to keep the order stable.
        if len(items) < self.limit:
            # The heap isn't full, so add this document
            heappush(items, (score, 0 - global_docnum))
            # Negate score to act as sort key so higher scores appear first
            return 0 - score
        elif score > items[0][0]:
            # The heap is full, but if this document has a high enough
            # score to make the top N, add it to the heap
            heapreplace(items, (score, 0 - global_docnum))
            self.minscore = items[0][0]
            # Negate score to act as sort key so higher scores appear first
            return 0 - score
        else:
            return 0

    def remove(self, global_docnum):
        negated = 0 - global_docnum
        items = self.items

        # Search through the results for the document and remove it
        for i in xrange(len(items)):
            if items[i][1] == negated:
                items.pop(i)
                # Restore the heap invariant
                heapify(items)
                self.minscore = items[0][0]
                return

        # The document wasn't on the list... somebody's confused!
        raise KeyError(global_docnum)

    def results(self):
        # The items are stored (postive score, negative docnum) so the heap
        # keeps the highest scores and lowest docnums, in order from lowest to
        # highest. Since for the results we want the highest scores first,
        # sort the heap in reverse order
        items = self.items
        items.sort(reverse=True)
        # De-negate the docnums for presentation to the user
        items = [(score, 0 - docnum) for score, docnum in items]
        return self._results(items)


class UnlimitedCollector(ScoredCollector):
    """A collector that only returns all scored results.
    """

    def __init__(self, reverse=False):
        ScoredCollector.__init__(self)
        self.reverse = reverse

    def _use_block_quality(self):
        return False

    # ScoredCollector.collect calls this
    def _collect(self, global_docnum, score):
        self.items.append((score, global_docnum))
        self.docset.add(global_docnum)
        # Negate score to act as sort key so higher scores appear first
        return 0 - score

    def results(self):
        # Sort by negated scores so that higher scores go first, then by
        # document number to keep the order stable when documents have the
        # same score
        self.items.sort(key=lambda x: (0 - x[0], x[1]), reverse=self.reverse)
        return self._results(self.items, docset=self.docset)


# Sorting collector

class SortingCollector(Collector):
    """A collector that returns results sorted by a given
    :class:`whoosh.sorting.Facet` object. See :doc:`/facets` for more
    information.
    """

    def __init__(self, sortedby, limit=10, reverse=False, **kwargs):
        """
        :param sortedby: see :doc:`/facets`.
        :param reverse: If True, reverse the overall results. Note that you
            can reverse individual facets in a multi-facet sort key as well.
        """

        Collector.__init__(self, **kwargs)
        self.sortfacet = sorting.MultiFacet.from_sortedby(sortedby)
        self.limit = limit
        self.reverse = reverse

    def prepare(self, top_searcher, q, requires_matcher=False):
        self.categorizer = self.sortfacet.categorizer(top_searcher)
        # If the categorizer requires a valid matcher, then tell the child
        # collector that we need it
        Collector.prepare(self, top_searcher, q,
                          self.categorizer.requires_matcher)
        # List of (sortkey, docnum) pairs
        self.items = []

    def set_subsearcher(self, subsearcher, offset):
        Collector.set_subsearcher(self, subsearcher, offset)
        self.categorizer.set_searcher(subsearcher, offset)

    def sort_key(self, sub_docnum):
        return self.categorizer.key_for(self.matcher, sub_docnum)

    def collect(self, sub_docnum):
        global_docnum = self.offset + sub_docnum
        sortkey = self.categorizer.key_for(self.matcher, sub_docnum)
        self.items.append((sortkey, global_docnum))
        self.docset.add(global_docnum)
        return sortkey

    def results(self):
        items = self.items
        items.sort(reverse=self.reverse)
        if self.limit:
            items = items[:self.limit]
        return self._results(items, docset=self.docset)


# Wrapping collectors

class WrappingCollector(Collector):
    """Base class for collectors that wrap other collectors.
    """

    def __init__(self, child):
        self.child = child

    def prepare(self, top_searcher, q, requires_matcher=False):
        self.child.prepare(top_searcher, q, requires_matcher)

    def set_subsearcher(self, subsearcher, offset):
        self.child.set_subsearcher(subsearcher, offset)

    def collect_matches(self):
        for sub_docnum in self.matches():
            self.collect(sub_docnum)

    def sort_key(self, sub_docnum):
        return self.child.sort_key(sub_docnum)

    def collect(self, sub_docnum):
        return self.child.collect(sub_docnum)

    def matches(self):
        return self.child.matches()

    def finish(self):
        self.child.finish()

    def results(self):
        return self.child.results()


# Allow and disallow collector

class FilterCollector(WrappingCollector):
    """A collector that lets you allow and/or restrict certain document numbers
    in the results::
    
        uc = collectors.UnlimitedCollector()
    
        ins = query.Term("chapter", "rendering")
        outs = query.Term("status", "restricted")
        fc = FilterCollector(uc, allow=ins, restrict=outs)
        
        mysearcher.search_with_collector(myquery, fc)
        print(fc.results())

    This collector discards a document if:
    
    * The allowed set is not None and a document number is not in the set, or
    * The restrict set is not None and a document number is in the set.
    
    (So, if the same document number is in both sets, that document will be
    discarded.)
    
    If you have a reference to the collector, you can use
    ``FilterCollector.filtered_count`` to get the number of matching documents
    filtered out of the results by the collector.
    """

    def __init__(self, child, allow=None, restrict=None):
        """
        :param child: the collector to wrap.
        :param allow: a query, Results object, or set-like object containing
            docnument numbers that are allowed in the results, or None (meaning
            everything is allowed).
        :param restrict: a query, Results object, or set-like object containing
            document numbers to disallow from the results, or None (meaning
            nothing is disallowed).
        """

        self.child = child
        self.allow = allow
        self.restrict = restrict

    def prepare(self, top_searcher, q, requires_matcher=False):
        self.child.prepare(top_searcher, q, requires_matcher)

        allow = self.allow
        restrict = self.restrict
        ftc = top_searcher._filter_to_comb

        self._allow = ftc(allow) if allow else None
        self._restrict = ftc(restrict) if restrict else None
        self.filtered_count = 0

    def collect_matches(self):
        child = self.child
        _allow = self._allow
        _restrict = self._restrict
        filtered_count = self.filtered_count

        for sub_docnum in child.matches():
            global_docnum = child.offset + sub_docnum
            if ((_allow and global_docnum not in _allow)
                or (_restrict and global_docnum in _restrict)):
                filtered_count += 1
                continue

            child.collect(sub_docnum)

        self.filtered_count = filtered_count

    def results(self):
        r = self.child.results()
        r.filtered_count = self.filtered_count
        r.allowed = self.allow
        r.restricted = self.restrict
        return r


# Facet grouping collector

class FacetCollector(WrappingCollector):
    """A collector that creates groups of documents based on
    :class:`whoosh.sorting.Facet` objects. See :doc:`/facets` for more
    information.
    
    This collector is used if you specify a ``groupedby`` parameter in the
    :meth:`whoosh.searching.Searcher.search` method. You can use the
    :meth:`whoosh.searching.Results.groups` method to access the facet groups.
    
    If you have a reference to the collector can also use
    ``FacetedCollector.facetmaps`` to access the groups directly::
    
        uc = collectors.UnlimitedCollector()
        fc = FacetedCollector(uc, sorting.FieldFacet("category"))
        mysearcher.search_with_collector(myquery, fc)
        print(fc.facetmaps)
    """

    def __init__(self, child, groupedby, maptype=None):
        """
        :param groupedby: see :doc:`/facets`.
        :param maptype: a :class:`whoosh.sorting.FacetMap` type to use for any
            facets that don't specify their own.
        """

        self.child = child
        self.facets = sorting.Facets.from_groupedby(groupedby)
        self.maptype = maptype

    def prepare(self, top_searcher, q, requires_matcher=False):
        facets = self.facets

        # For each facet we're grouping by:
        # - Create a facetmap (to hold the groups)
        # - Create a categorizer (to generate document keys)
        self.facetmaps = {}
        self.categorizers = {}
        # True if any of the categorizers require the matcher to work
        reqm = requires_matcher
        for facetname, facet in facets.items():
            self.facetmaps[facetname] = facet.map(self.maptype)

            ctr = facet.categorizer(top_searcher)
            self.categorizers[facetname] = ctr
            if ctr.requires_matcher:
                reqm = True

        # If any of the categorizers require the matcher, tell the child
        # collector we need it
        self.child.prepare(top_searcher, q, reqm)

    def set_subsearcher(self, subsearcher, offset):
        child = self.child
        child.set_subsearcher(subsearcher, offset)

        # Tell each categorizer about the new subsearcher and offset
        for categorizer in itervalues(self.categorizers):
            categorizer.set_searcher(child.subsearcher, child.offset)

    def collect(self, sub_docnum):
        matcher = self.child.matcher
        global_docnum = sub_docnum + self.child.offset

        # We want the sort key for the document so we can (by default) sort
        # the facet groups
        sortkey = self.child.collect(sub_docnum)

        # For each facet we're grouping by
        for name, categorizer in iteritems(self.categorizers):
            add = self.facetmaps[name].add

            # We have to do more work if the facet allows overlapping groups
            if categorizer.allow_overlap:
                for key in categorizer.keys_for(matcher, sub_docnum):
                    add(categorizer.key_to_name(key), global_docnum, sortkey)
            else:
                key = categorizer.key_for(matcher, sub_docnum)
                key = categorizer.key_to_name(key)
                add(key, global_docnum, sortkey)

        return sortkey

    def results(self):
        r = self.child.results()
        r._facetmaps = self.facetmaps
        return r


# Collapsing collector

class CollapseCollector(WrappingCollector):
    """A collector that collapses results based on a facet. That is, it
    eliminates all but the top N results that share the same facet key.
    Documents with an empty key for the facet are never eliminated.
    
    The "top" results within each group is determined by the result ordering
    (e.g. highest score in a scored search) or an optional second "ordering"
    facet.
    
    If you have a reference to the collector can also use
    ``CollapseCollector.collapsed_counts`` to access the number of documents
    eliminated based on each key::
    
        tc = TopCollector(limit=20)
        cc = CollapseCollector(tc, "group", limit=3)
        mysearcher.search_with_collector(myquery, cc)
        print(cc.collapsed_counts)
    
    See :ref:`collapsing` for more information.
    """

    def __init__(self, child, keyfacet, limit=1, order=None):
        """
        :param child: the collector to wrap.
        :param keyfacet: a :class:`whoosh.sorting.Facet` to use for collapsing.
            All but the top N documents that share a key will be eliminated
            from the results.
        :param limit: the maximum number of documents to keep for each key.
        :param orderfacet: an optional :class:`whoosh.sorting.Facet` to use
            to determine the "top" document(s) to keep when collapsing. The
            default (``orderfaceet=None``) uses the results order (e.g. the
            highest score in a scored search).
        """

        self.child = child
        self.keyfacet = sorting.MultiFacet.from_sortedby(keyfacet)

        self.limit = limit
        if order:
            self.orderfacet = sorting.MultiFacet.from_sortedby(order)
        else:
            self.orderfacet = None

    def prepare(self, top_searcher, q, requires_matcher=False):
        # Categorizer for getting the collapse key of a document
        self.keyer = self.keyfacet.categorizer(top_searcher)
        # Categorizer for getting the collapse order of a document
        self.orderer = None
        if self.orderfacet:
            self.orderer = self.orderfacet.categorizer(top_searcher)

        # Dictionary mapping keys to lists of (sortkey, global_docnum) pairs
        # representing the best docs for that key
        self.lists = defaultdict(list)
        # Dictionary mapping keys to the number of documents that have been
        # filtered out with that key
        self.collapsed_counts = defaultdict(int)

        # If the keyer or orderer require a valid matcher, tell the child
        # collector we need it
        reqm = (self.keyer.requires_matcher
                or (self.orderer and self.orderer.requires_matcher))
        self.child.prepare(top_searcher, q, reqm)

    def set_subsearcher(self, subsearcher, offset):
        self.child.set_subsearcher(subsearcher, offset)
        self.keyer.set_searcher(subsearcher, offset)
        if self.orderer:
            self.orderer.set_searcher(subsearcher, offset)

    def collect_matches(self):
        lists = self.lists
        limit = self.limit
        keyer = self.keyer
        orderer = self.orderer
        collapsed_counts = self.collapsed_counts

        child = self.child
        offset = child.offset
        for sub_docnum in child.matches():
            # Collapsing category key
            ckey = keyer.key_to_name(keyer.key_for(child.matcher, sub_docnum))
            if ckey is None:
                # If the document isn't in a collapsing category, just add it
                child.collect(sub_docnum)
            else:
                global_docnum = offset + sub_docnum

                if orderer:
                    # If user specified a collapse order, use it
                    sortkey = orderer.key_for(child.matcher, sub_docnum)
                else:
                    # Otherwise, use the results order
                    sortkey = child.sort_key(sub_docnum)

                # Current list of best docs for this collapse key
                best = lists[ckey]
                add = False
                if len(best) < limit:
                    # If the heap is not full yet, just add this document
                    add = True
                elif sortkey < best[-1][0]:
                    # If the heap is full but this document has a lower sort
                    # key than the highest key currently on the heap, replace
                    # the "least-best" document
                    # Tell the child collector to remove the document
                    child.remove(best.pop()[1])
                    # Remember that a document was filtered
                    collapsed_counts[ckey] += 1
                    add = True

                if add:
                    insort(best, (sortkey, global_docnum))
                    child.collect(sub_docnum)
                else:
                    # Remember that a document was filtered
                    collapsed_counts[ckey] += 1

    def results(self):
        r = self.child.results()
        r.collapsed_counts = self.collapsed_counts
        return r


# Time limit collector

class TimeLimitCollector(WrappingCollector):
    """
    A collector that raises a :class:`TimeLimit` exception if the search
    does not complete within a certain number of seconds::
    
        uc = collectors.UnlimitedCollector()
        tlc = TimeLimitedCollector(uc, timelimit=5.8)
        try:
            mysearcher.search_with_collector(myquery, tlc)
        except collectors.TimeLimit:
            print("The search ran out of time!")
        
        # We can still get partial results from the collector
        print(tlc.results())
    
    """

    def __init__(self, child, timelimit, greedy=False):
        """
        :param child: the collector to wrap.
        :param timelimit: the maximum amount of time (in seconds) to allow
            for searching. If the search takes longer than this, it will raise
            a ``TimeLimit`` exception.
        :param greedy: if ``True``, the collector will finish adding the most
            recent hit before raising the ``TimeLimit`` exception.
        """
        self.child = child
        self.timelimit = timelimit
        self.greedy = greedy

    def prepare(self, top_searcher, q, requires_matcher=False):
        self.child.prepare(top_searcher, q, requires_matcher)

        # Start a timer thread. If the timer fires, it will call this object's
        # _timestop() method
        self.timedout = False
        self.timer = threading.Timer(self.timelimit, self._timestop)
        self.timer.start()

    def _timestop(self):
        self.timer = None
        # Set an attribute that will be noticed in the collect_matches() loop
        self.timedout = True

    def collect_matches(self):
        child = self.child
        greedy = self.greedy

        for sub_docnum in child.matches():
            # If the timer fired since the last loop and we're not greedy,
            # raise the exception
            if self.timedout and not greedy:
                raise TimeLimit

            child.collect(sub_docnum)

            # If the timer fired since we entered the loop or it fired earlier
            # but we were greedy, raise now
            if self.timedout:
                raise TimeLimit

    def finish(self):
        if self.timer:
            self.timer.cancel()
        self.timer = None
        self.child.finish()


# Matched terms collector

class TermsCollector(WrappingCollector):
    """A collector that remembers which terms appeared in which terms appeared
    in each matched document.
    
    This collector is used if you specify ``terms=True`` in the
    :meth:`whoosh.searching.Searcher.search` method.
    
    If you have a reference to the collector can also use
    ``TermsCollector.termslist`` to access the term lists directly::
    
        uc = collectors.UnlimitedCollector()
        tc = TermsCollector(uc)
        mysearcher.search_with_collector(myquery, tc)
        # tc.termdocs is a dictionary mapping (fieldname, text) tuples to
        # sets of document numbers
        print(tc.termdocs)
        # tc.docterms is a dictionary mapping docnums to lists of
        # (fieldname, text) tuples
        print(tc.docterms)
    """

    def __init__(self, child, settype=set):
        self.child = child
        self.settype = settype

    def prepare(self, top_searcher, q, requires_matcher=False):
        # This collector requires a valid matcher at each step
        self.child.prepare(top_searcher, q, True)

        # A dictionary mapping (fieldname, text) pairs to arrays of docnums
        self.termdocs = defaultdict(lambda: array("I"))
        # A dictionary mapping docnums to lists of (fieldname, text) pairs
        self.docterms = defaultdict(list)

    def set_subsearcher(self, subsearcher, offset):
        child = self.child
        child.set_subsearcher(subsearcher, offset)
        # Store a list of all the term matchers in the matcher tree
        self.termmatchers = list(child.matcher.term_matchers())

    def collect(self, sub_docnum):
        child = self.child
        termdocs = self.termdocs
        docterms = self.docterms

        child.collect(sub_docnum)

        global_docnum = child.offset + sub_docnum
        # For each term matcher...
        for tm in self.termmatchers:
            # If the term matcher is matching the current document...
            if tm.is_active() and tm.id() == sub_docnum:
                # Add it to the list of matching documents for the term
                term = tm.term()
                termdocs[term].append(global_docnum)
                docterms[global_docnum].append(term)

    def results(self):
        r = self.child.results()
        r.termdocs = dict(self.termdocs)
        r.docterms = dict(self.docterms)
        return r



