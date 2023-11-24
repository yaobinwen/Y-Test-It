# Zuustand

## Background

Refer to the "Background" section of `kombii`'s [`README.md`](../kombii/README.md).

`kombii` solves the problem of figuring out all the states that need to be tested under certain constraints. In the problem of "IPv4/IPv6 address/DNS assignment", `kombii` can help me cover all the valid combinations of the IPv4/IPv6 address/DNS configuration I need to test.

However, the other part of the "IPv4/IPv6 address/DNS assignment" feature was the GUI. The GUI needs to be implemented correctly so it can correctly transition from one configuration to another configuration. For example, when we disable the IPv4 stack entirely, we should also disable the IPv4 address and DNS input boxes; but when we re-enable the IPv4 stack, we should also re-enable the IPv4 address and DNS input boxes so the users can enter them. This example involves two state changes:
- Changing from "IPv4 stack enabled" to "IPv4 stack disabled".
- Changing from "IPv4 stack disabled" to "IPv4 stack enabled".

The GUI testing wants to make sure that all such valid transitions are implemented; there is no missing transition; there is incorrect transition. Now the question is: when there are many possible states and transitions among states, how can I make sure I cover all the needed transitions and don't miss any?

This problem space can be extracted as a graph. Using the example above, "IPv4 stack enabled" and "IPv4 stack disabled" are two vertices (which `kombii` can find) on a graph. "Changing from 'IPv4 stack enabled' to 'IPv4 stack disabled'" and "changing from 'IPv4 stack disabled' to 'IPv4 stack enabled'" are two directed edges that connect these two vertices on the graph. Covering all the transitions is essentially traversing all the edges on the graph.

To minimize the testing effort, we want to traverse every edge only once, ideally. Traversing all the edges on a graph exactly once can be solved by finding the [Eulerian path](https://en.wikipedia.org/wiki/Eulerian_path) (or even the Eulerian cycle) on the graph. However, not every graph has an Eulerian path. Even if a graph has an Eulerian path, to follow the Eulerian path, we have to start with the vertices that have odd degrees. But in reality, we may not be able to start with those vertices. In the IPv4/IPv6 configuration example, maybe we must always start with the state of "IPv4 enabled; IPv4 address/DNS assignment as Auto; IPv6 enabled; IPv6 address/DNS assignment as Auto". If the corresponding vertex on the graph has an even degree, even if the graph has an Eulerian path, we can't traverse all the edges exactly once.

So these are the problems that `zuustand` tries to solve:
- 1). Given the valid states (i.e., the vertices) and the constraints that the transitions (i.e., the edges) must meet, generate the graph.
- 2). Figure out the paths that start with specified states and can cover all the transitions. Test engineers can follow these paths to cover all the valid state transitions to achieve 100% coverage.

## About the name

`Zuustand` is a variant of the German word ["Zustand"](https://dictionary.cambridge.org/dictionary/german-english/zustand) which means "state" (as the "state" in a "state diagram"). Unlike many state diagram software products that depend on the users to figure out the diagram by themselves, `zuustand` asks the users to provide the states and the constraints that the transitions must meet, and `zuustand` generates the state diagram for the users. Because the fundamental data structure is the "state diagram", I chose the German word "Zustand" to name it.

## How to use

(TODO)

## TODOs

- Simple tests showed it should work (to some extent). Need more testing to make sure it really works.
- Need more unit tests.
- Need more documentation and comments to the code.
