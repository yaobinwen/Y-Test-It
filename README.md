# Y-Test-It

## 1. Overview

"Y" is the first letter of my given name and "Y-Test-It" sounds like "why test it".

This is my repository to keep notes about software testing theories and practices, as well as the code for tools.

## 2. Tools: `kombii` and `zuustand`

The tools `kombii` and `zuustand` are suitable for some (not all) problems that can be abstracted as **finite-state machines**. See [this Wikipedia article](https://en.wikipedia.org/wiki/Finite-state_machine) and [this MDN article](https://developer.mozilla.org/en-US/docs/Glossary/State_machine) for what a finite-state machine is.

A finite-state machine consists of, of course, "states". A state can be described by the particular choices of values of one or more variables.

But `kombii` and `zuustand` are not tools for general state machine problems. I created them in some particular context.

Given an array of variables and all their possible values, `kombii` generates combinations of all the variables of all the possible values based on given constraints (so the combinations that do not meet the constraints are dropped).

When the total number of all the combinations is large, it's usually not practical to test all the cases. However, if the total number is relatively small, testing all of the test cases should still be considered. Pairwise testing is a widely used method to reduce the needed number of test cases for combinatorial testing problems, and is often seen as the replacement of testing all the combinations. However, pairwise testing, if used inappropriately, is not as effective as one may expect. See the section "Illusion of pairwise testing."

## 3. Tool: `zuustand`

Given an array of states (which are usually the output of `kombii`) and the constraints that the state transitions must meet, `zuustand` generates the state diagram as a directed graph. `zuustand` also provides APIs to find the paths that start with certain states and cover all the transitions. Test engineers can follow these paths to test their products to make sure they cover all the possible state transitions.

## 4. Illusion of pairwise testing

[Pairwise testing](https://en.wikipedia.org/wiki/All-pairs_testing) is widely considered as a "best practice" because it can significantly reduce the number of needed test cases when the number of the full combination is large. However, in the paper [Pairwise Testing: A Best Practice That Isn't (by James Bach and Patrick J. Schroeder)](https://www.satisfice.com/download/pairwise-testing-a-best-practice-that-isnt)(which I saved a copy [here](./papers/Pairwise-Testing_A-Best-Practice-That-Isnt.pdf)), the authors argue that instead of "blindly applying pairwise testing as a 'best practice' in all combinatorial testing situations, we should be **analyzing the software being tested**, **determining how inputs are combined to create outputs** and
**how these operations could fail**," in order to apply "an appropriate combinatorial testing strategy."

The paper lists four major reasons that can cause pairwise testing to fail:
- "Pairwise testing fails when you don't select the right values to test with."
- "Pairwise testing fails when you don't have a good enough oracle."
- "Pairwise testing fails when highly probable combinations get too little attention."
- "Pairwise testing fails when you don't know how the variables interact."

In other words, pairwise testing is effective when all of the following conditions are met:
- The equivalence classes of the input values are **truly equivalent**, i.e., assuming the software is implemented correctly, the values in the same equivalence class either all succeed or all fail.
- Being the tester, given the output of an input, you can confidently determine whether the output reveals a bug or not, i.e., **no false positives or false negatives.**
- The probability of all the combinations is an **even** distribution.
- The outputs of the code under test are created by the interaction of **no more than two (i.e., a pair of)** input variables.

As a result, the test problems that are suitable for pairwise testing are not as many as one may think.
