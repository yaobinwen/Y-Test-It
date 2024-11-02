# Y-Test-It

## 1. Overview

"Y" is the first letter of my given name and "Y-Test-It" sounds like "why test it".

This is my repository to keep notes about software testing theories and practices, as well as the code for tools.

## 2. Tools: `kombii` and `zuustand`

### 2.1 Background

I came up with the idea of `kombii` and `zuustand` when I was working on the testing of a software feature in my work. Basically, this feature includes a GUI and a backend service that work together to allow the user to configure a particular network interface on the computer systems. The user uses the GUI to specify the configuration he/she wants to apply to the network interface; the GUI passes the user's choices to the backend service which generates the configuration files and makes the configuration effective.

The user is allowed to configure the network interface as follows:
- Enable or disable the entire IPv4 stack. When IPv4 is enabled, the user can further specify whether the IPv4 address (including the netmask and the route) should be automatically obtained from the DHCP servers or should be manually entered; the user can also specify whether the IPv4 DNS servers should be automatically obtained from the DHCP servers or should be manually entered.
- Enable or disable the entire IPv6 stack. When IPv6 is enabled, the user can further specify whether the IPv6 address (including the netmask and the route) should be automatically obtained from the DHCP servers or should be manually entered; the user can also specify whether the IPv6 DNS servers should be automatically obtained from the DHCP servers or should be manually entered.

If you have a laptop that runs Windows/Mac/Linux desktop, you will surely have the network settings somewhere. You can open the network setting GUI on your desktop and see what you can configure in order to get some sense of the feature I wanted to test. They are not the same but quite similar.

Now, I needed to make sure the generated configuration worked as expected. I also needed to make sure the GUI was implemented correctly to allow the user to configure the network interface as desired. **Question to the readers**: When you need to test a feature, you need to figure out the test cases to run. How would you plan your tests if you were going to test the same software feature as I did?

### 2.2 The state machine

My mathematical model of the testing problem I had in 2.1 was as follows.

#### 2.2.1 The backend

First of all, I needed to find all the practically possible network interface configurations and make sure I tested all of them. A "practically possible" configuration was one that made sense in the context. For example, the user may choose to configure the network interface this way: IPv4 stack entirely disabled; IPv6 enabled; DHCP IPv6 address assignment; manually specified IPv6 DNS servers.

However, the following configurations didn't make sense:
- IPv4 was entirely enabled but still used DHCP for IPv4 address assignment and IPv4 DNS server assignment.
- IPv4 was enabled; IPv4 address was specified manually (so no DHCP server would be used) but still wanted to use DHCP for IPv4 DNS server assignment.

Therefore, my first task was to list all the practically possible configurations. To do that, I could simply apply the rule of product: I figured a valid network interface configuration consisted of the following variables:

| Configuration item                | Possible states           | Number of possible states |
|----------------------------------:|:--------------------------|:-------------------------:|
| IPv4 stack                        | enabled; disabled         | 2                         |
| IPv4 IP address assignment method | auto (i.e., DHCP); manual | 2                         |
| IPv4 DNS assignment method        | auto; manual              | 2                         |
| IPv6 stack                        | enabled; disabled         | 2                         |
| IPv6 IP address assignment method | auto (i.e., DHCP); manual | 2                         |
| IPv6 DNS assignment method        | auto; manual              | 2                         |

To get a full testing coverage, I wanted to test all the possible cases. If we don't consider the inter-dependencies of the 6 configuration items, the number of the full combination of them is $2 \times 2 \times 2 \times 2 \times 2 \times 2 = 2^6 = 64$. But because the configuration items can affect each other, the actual number of valid combinations is not equal to the number of the full combination. The validity of the test cases is based on the following constraints:
- IPv4 IP address assignment method and IPv4 DNS assignment method are applicable only if IPv4 stack is enabled.
- When IPv4 IP address assignment method is "manual" (i.e., not using any DHCP server), IPv4 DNS assignment method must be "manual" as well (i.e., it makes no sense to not use any DHCP servers but still want DHCP-assigned DNS servers).
- IPv6 IP address assignment method and IPv6 DNS assignment method are applicable only if IPv6 stack is enabled.
- When IPv6 IP address assignment method is "manual" (i.e., not using any DHCP server), IPv6 DNS assignment method must be "manual" as well (i.e., it makes no sense to not use any DHCP servers but still want DHCP-assigned DNS servers).

Surely I could list all the possible 64 test cases and then remove those that don't make sense, but then I started to think: **Is there any tool that can generate combinatorial test cases based on constraints?** There doesn't seem so after a quick search (well, [this page](https://github.com/jaccz/pairwise/blob/main/tools.md) lists a bunch of tools but those that may offer the wanted functions, such as "CATS (Constrained Array Test System)" and "CTS (Combinatorial Test Services)", can no longer be opened), so I decided to write my own, hence the creation of `kombii`.

#### 2.2.2 The GUI

Every practically possible network interface configuration was specified by the user on the GUI. In other words, the GUI must be able to get into all the states that can generate all the practically possible network interface configurations. Therefore, there was a one-on-one correspondence between the GUI states and the network interface configurations.

When the user operated the GUI, the user was essentially transitioning from one practically possible network interface to another. This can be modeled as a state machine.

The state machine was essentially a graph: every state was a vertex on the graph; the directed transitions were the directed edges on the graph. Then I got the second question: In order to make sure the I tested all the valid transitions, how should I traverse all the states in order to minimize the total number of transitions? `zuustand` was implemented to find the solution.

### 2.3 Limitation

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

## 5. Classification Tree Method (CTM)

See [_Wikipedia: Classification Tree Method_](https://en.wikipedia.org/wiki/Classification_Tree_Method).

## 6. Testing Coverage

See [NASA: A Practical Tutorial on Modified Condition/Decision Coverage](https://ntrs.nasa.gov/citations/20010057789). A downloaded version is available at [`./papers/NASA-A-Practical-Tutorial-on-MCDC-Coverage.pdf`](./papers/NASA-A-Practical-Tutorial-on-MCDC-Coverage.pdf).
