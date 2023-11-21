# kombii: Generate full or conditional combinatorial test cases

## Background

I came up with the idea of `kombii` when I was working on the test cases of a product feature in my work. The feature is essentially a network configuration GUI which allows the user to configure the network interface as follows:

| Configuration item                | Possible states           |
|----------------------------------:|:--------------------------|
| IPv4 stack                        | enabled; disabled         |
| IPv4 IP address assignment method | auto (i.e., DHCP); manual |
| IPv4 DNS assignment method        | auto; manual              |
| IPv6 stack                        | enabled; disabled         |
| IPv6 IP address assignment method | auto (i.e., DHCP); manual |
| IPv6 DNS assignment method        | auto; manual              |

To get a full testing coverage, I wanted to test all the possible cases. If we don't consider the inter-dependencies of the 6 configuration items, the number of the full combination of them is $2 \times 2 \times 2 \times 2 \times 2 \times 2 = 2^6 = 64$. But because the configuration items can affect each other, the actual number of valid combinations is not equal to the number of the full combination. The validity of the test cases is based on the following constraints:
- IPv4 IP address assignment method and IPv4 DNS assignment method are applicable only if IPv4 stack is enabled.
- When IPv4 IP address assignment method is "manual" (i.e., not using any DHCP server), IPv4 DNS assignment method must be "manual" as well (i.e., it makes no sense to not use any DHCP servers but still want DHCP-assigned DNS servers).
- IPv6 IP address assignment method and IPv6 DNS assignment method are applicable only if IPv6 stack is enabled.
- When IPv6 IP address assignment method is "manual" (i.e., not using any DHCP server), IPv6 DNS assignment method must be "manual" as well (i.e., it makes no sense to not use any DHCP servers but still want DHCP-assigned DNS servers).

Surely I could list all the possible 64 test cases and then remove those that don't make sense, but then I started to think: **Is there any tool that can generate combinatorial test cases based on constraints?** There doesn't seem so after a quick search (well, [this page](https://github.com/jaccz/pairwise/blob/main/tools.md) lists a bunch of tools but those that may offer the wanted functions, such as "CATS (Constrained Array Test System)" and "CTS (Combinatorial Test Services)", can no longer be opened), so I decided to write my own, hence the creation of `kombii`.

## How to use

See [examples/ipv4_ipv6.py](./examples/ipv4_ipv6.py) which implements the constraints in the "Background" section.

To run it, `cd` into `examples` and run `PYTHONPATH="../src" python3 -m ipv4_ipv6`, and it prints all the valid test cases (12 in total) under the given constraints:

```
1: {'v4_enabled': False, 'v6_enabled': False, 'v4_ip': 'N/A', 'v4_dns': 'N/A', 'v6_ip': 'N/A', 'v6_dns': 'N/A'}
2: {'v4_enabled': False, 'v6_enabled': True, 'v4_ip': 'N/A', 'v4_dns': 'N/A', 'v6_ip': 'Auto', 'v6_dns': 'Auto'}
3: {'v4_enabled': False, 'v6_enabled': True, 'v4_ip': 'N/A', 'v4_dns': 'N/A', 'v6_ip': 'Auto', 'v6_dns': 'Manual'}
4: {'v4_enabled': False, 'v6_enabled': True, 'v4_ip': 'N/A', 'v4_dns': 'N/A', 'v6_ip': 'Manual', 'v6_dns': 'Manual'}
5: {'v4_enabled': True, 'v6_enabled': False, 'v4_ip': 'Auto', 'v4_dns': 'Auto', 'v6_ip': 'N/A', 'v6_dns': 'N/A'}
6: {'v4_enabled': True, 'v6_enabled': False, 'v4_ip': 'Auto', 'v4_dns': 'Manual', 'v6_ip': 'N/A', 'v6_dns': 'N/A'}
7: {'v4_enabled': True, 'v6_enabled': False, 'v4_ip': 'Manual', 'v4_dns': 'Manual', 'v6_ip': 'N/A', 'v6_dns': 'N/A'}
8: {'v4_enabled': True, 'v6_enabled': True, 'v4_ip': 'Auto', 'v4_dns': 'Auto', 'v6_ip': 'Auto', 'v6_dns': 'Auto'}
9: {'v4_enabled': True, 'v6_enabled': True, 'v4_ip': 'Auto', 'v4_dns': 'Manual', 'v6_ip': 'Auto', 'v6_dns': 'Manual'}
10: {'v4_enabled': True, 'v6_enabled': True, 'v4_ip': 'Auto', 'v4_dns': 'Manual', 'v6_ip': 'Manual', 'v6_dns': 'Manual'}
11: {'v4_enabled': True, 'v6_enabled': True, 'v4_ip': 'Manual', 'v4_dns': 'Manual', 'v6_ip': 'Auto', 'v6_dns': 'Manual'}
12: {'v4_enabled': True, 'v6_enabled': True, 'v4_ip': 'Manual', 'v4_dns': 'Manual', 'v6_ip': 'Manual', 'v6_dns': 'Manual'}
```
