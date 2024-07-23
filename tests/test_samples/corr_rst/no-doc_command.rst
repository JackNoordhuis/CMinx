
###################
no-doc-command test
###################

.. module:: no-doc-command test

   
   This test case makes sure the `@module` command has priority when
   appearing before `@no-doc`. A `@no-doc` should only appear as a
   replacement to `@module`, not alongside it.
   
   @no-doc
   
   This test also verifies the escaped space is maintained and the `case`
   parameter does not appear in the module name.
   
   


.. function:: documented_function()

   This is a documented function
   
   @no-doc
   


.. function:: documented_macro()


   .. note:: This is a macro, and so does not introduce a new scope.

   This is a documented macro
   
   @no-doc
   

