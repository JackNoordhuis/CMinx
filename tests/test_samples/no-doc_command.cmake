#[[[ @module no-doc-command\ test case
#
# This test case makes sure the `@module` command has priority when
# appearing before `@no-doc`. A `@no-doc` should only appear as a
# replacement to `@module`, not alongside it.
#
# @no-doc
#
# This test also verifies the escaped space is maintained and the `case`
# parameter does not appear in the module name.
#
#]]


#[[[ @no-doc
# This is an undocumented command invocation
#]]
include_guard()

#[[[ @no-doc
#]]
option("UNDOCUMENTED" "???")

#[[[
# This is an undocumented function
#
# @no-doc
#]]
function(undocumented_function)
endfunction()

#[[[
# This is an undocumented macro
#
# @no-doc
#
# With more text
#]]
macro(undocumented_macro)
endmacro()

#[[[
# This is a documented function
#
# \@no-doc
#]]
function(documented_function)
endfunction()

#[[[
# This is a documented macro
#
# \@no-doc
#]]
macro(documented_macro)
endmacro()