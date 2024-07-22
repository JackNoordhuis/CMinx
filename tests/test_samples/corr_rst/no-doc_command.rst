
###################
no-doc-command test
###################

.. module:: no-doc-command test

   This test case makes sure the `@module` command has priority when
   appearing before `@no-doc`. A `@no-doc` should only appear as a
   replacement to `@module`, not alongside it.

   This test also verifies the escaped space is maintained and the `case`
   parameter does not appear in the module name.



.. function:: documented_function()

   This is a documented function

   @no-doc



.. macro:: documented_macro()

   This is a documented macro

   @no-doc



