from iblt import IBLT

t = IBLT( 30, 4, 10, 10 )
assert t.is_empty()

# Test if inserting and deleting the same pair in an empty table
# results in an empty table again
t.insert( "testkey", "testvalue" )
t.insert( "testkey", "testval" )
t.delete( "testkey", "testvalue" )
t.delete( "testkey", "testval" )
assert t.is_empty()


# Test if inserting 10 key/value pairs can be listed out
pairs = [( "key%d" % i, "value%d" % i ) for i in range( 10 )]
for key, value in pairs:
	t.insert( key, value )
entries = t.list_entries()
assert entries[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
# Get set intersection, should contain all elements from pairs
intersect = set(pairs) & set(entries[1])
assert set( pairs ) == intersect
# Get set union, should contain only the elements from pairs
union = set(pairs) | set(entries[1])
assert set( pairs ) == union

#Test if 2 arrays can successfully be subtracted 
t1 = IBLT( 10, 4, 10, 10)
t2 = IBLT( 10, 4, 10, 10)
pairs1 = [( "key%d" % i, "value%d" % i ) for i in range(1,10 )]
for key, value in pairs1:
	t1.insert( key, value )
pairs2 = [( "key%d" % i, "value%d" % i ) for i in range(4,12)]
for key, value in pairs2:
        t2.insert( key, value )
arr3= t1.subtract(t1.T,t2.T)
print t1.list_entries()

# Test if deleting a key/value pair that hasn't been inserted before
# doesn't result in bad list_entries() or get()
t = IBLT( 30, 4, 10, 10 )
t.delete( "delkey", "delval" )
t.insert( "inskey", "insval" )
entries = t.list_entries()
assert entries[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE
# One inserted entry
assert len( entries[1] ) == 1
assert entries[1][0] == ( "inskey", "insval" )
# One deleted entry
assert len( entries[2] ) == 1
assert entries[2][0] == ( "delkey", "delval" )
assert t.get( "inskey" ) == ( IBLT.RESULT_GET_MATCH, "insval" )
assert t.get( "delkey" ) == ( IBLT.RESULT_GET_DELETED_MATCH, "delval" )


# Test if inserting more that m=30 keys/values will result in an incomplete listing
# and then remove some of them again to get a complete listing
t = IBLT( 30, 4, 10, 10 )
pairs = [( "key%d" % i, "value%d" % i ) for i in range( 1031 )]
for key, value in pairs:
	t.insert( key, value )

assert t.list_entries()[0] == IBLT.RESULT_LIST_ENTRIES_INCOMPLETE
pairs_to_keep = pairs[:15]
pairs_to_delete = pairs[15:]
for key, value in pairs_to_delete:
	t.delete( key, value )

entries = t.list_entries()
assert entries[0] == IBLT.RESULT_LIST_ENTRIES_COMPLETE

assert len( entries[1] ) == len( pairs_to_keep )
# Check if returned entries are the same as in pairs_to_keep
assert len( set( entries[1] ).difference( set( pairs_to_keep ) ) ) == 0
# Check that returned entries contains none of the pairs_to_delete
assert len( set( entries[1] ).intersection( set( pairs_to_delete ) ) ) == 0


# Test that serializing and unserializing works
assert t == IBLT.unserialize( t.serialize() )
