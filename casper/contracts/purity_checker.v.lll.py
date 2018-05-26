## This Python source code hosts the Vyper LLL used for the purity checker.
## The purity checker scans a contract's bytecode to see if it uses any operations that rely on (external) mutable state.
## This functionality is used in Casper to make sure a validator's signature verification code is "pure" so that the Casper contract can determine the authenticity of messages without reference to additional external state.

# NOTE: the following code is untested and probably contains bugs.
purity_checker_lll = ["seq",
                      ["return",
                       0,
                       ["lll",
                        ["seq",
                         ["mstore", 28, ["calldataload", 0]],
                         ["mstore", 32, 1461501637330902918203684832716283019655932542976],
                         ["mstore", 64, 170141183460469231731687303715884105727],
                         ["mstore", 96, -170141183460469231731687303715884105728],
                         ["mstore", 128, 1701411834604692317316873037158841057270000000000],
                         ["mstore", 160, -1701411834604692317316873037158841057280000000000],
                         ["if",
                          ["eq", ["mload", 0], 2710585003], # submit
                          ["seq",
                           # MEMORY MAP
                           # [320, 351]: addr, the input address, 32 bytes
                           # [352, 352+_EXTCODESIZE-1]: bytecode at addr, _EXTCODESIZE bytes
                           # [352+_EXTCODESIZE, 352+2*_EXTCODESIZE-1]: ops, array to hold processed opcodes, _EXTCODESIZE bytes
                           # [352+2*_EXTCODESIZE, 352+3*_EXTCODESIZE-1]: pushargs, array to hold processed push arguments, _EXTCODESIZE bytes
                           # [352+3*_EXTCODESIZE, 384+3*_EXTCODESIZE-1]: i, loop counter, 32 bytes
                           ["calldatacopy", 320, 4, 32],
                           ["assert", ["iszero", "callvalue"]],
                           ["uclamplt", ["calldataload", 4], ["mload", 32]], # checking address input
                           ["with", "_EXTCODESIZE", ["extcodesize", ["mload", 320]], # addr
                            ["seq",
                             ["extcodecopy", ["mload", 320], 352, 0, "_EXTCODESIZE"],
                             ["with", "_i", ["add", 352, ["mul", 3, "_EXTCODESIZE"]],
                              ["seq",
                               ["with", "_op", 0,
                                ["seq",
                                 ["repeat", "_i", 0, 115792089237316195423570985008687907853269984665640564039457584007913129639936,
                                  ["if", ["ge", ["mload", "_i"], "_EXTCODESIZE"],
                                   "break",
                                   ["with", "_c", ["mod", ["mload", ["add", 352, ["sub", "_i", 31]]], 256],
                                    ["seq",
                                     ["if",
                                      ["and", 57897811465722876096115075801844696845150819816717216876035649536196444422144,
                                       ["exp", 2, "_c"]],
                                      "invalid"],
                                     ["if",
                                      ["and", ["le", 0x60, "_c"], ["le", "_c", 0x7f]],
                                      ["seq",
                                       ["mstore8", ["add", ["add", 352, ["mul", 2, "_EXTCODESIZE"]], "_op"], ["div", ["mload", ["add", ["add", 352, "_i"], 1]], ["exp", 256, ["sub", 0x7f, "_c"]]]],
                                       ["mstore", "_i", ["add", ["sub", "_c", 0x5e], ["mload", "_i"]]]],
                                      ["if",
                                       ["or", ["eq", "_c", 0xf1],
                                        ["or", ["eq", "_c", 0xf2], ["eq", "_c", 0xf4]]],
                                       ["with", "_address_entry", 0,
                                        ["seq",
                                         ["if", ["and", ["ge", "_op", 2],
                                                 ["and", ["ge", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x60],
                                                  ["le", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x7f]]],
                                          ["set", "_address_entry", ["sub", "_op", 2]],
                                          ["if",
                                           ["and", ["ge", "_op", 4],
                                            ["and", ["eq", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x03],
                                             ["and", ["eq", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 2]]], 0x5a],
                                              ["and", ["ge", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 3]]], 0x60],
                                               ["le", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 3]]], 0x7f]]]]],
                                           ["set", "_address_entry", ["sub", "_op", 4]],
                                           ["if", ["and", ["ge", "_op", 2],
                                                   ["eq", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x5a]],
                                            ["set", "_address_entry", ["sub", "_op", 2]],
                                            ["if", ["and", ["ge", "_op", 2],
                                                    ["eq", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x90]],
                                             ["set", "_address_entry", ["sub", "_op", 2]],
                                             ["if", ["and", ["ge", "_op", 2],
                                                     ["and", ["ge", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x80],
                                                      ["lt", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], ["sub", "_op", 1]]], 0x90]]],
                                              ["set", "_address_entry", ["sub", "_op", 2]],
                                              "invalid"]]]]],
                                         ["if", ["sload",
                                                 ["add", ["sha3_32", 0], # self.approved_addrs
                                                  ["mload", ["add", ["add", 352, ["mul", 2, "_EXTCODESIZE"]], "_address_entry"]]]],
                                          ["seq"],
                                          ["if", ["eq", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], "_address_entry"]], 0x30],
                                           ["seq"],
                                           ["if", ["eq", ["mload", ["add", ["add", 352, "_EXTCODESIZE"], "_address_entry"]], 0x60],
                                            ["seq"],
                                            "invalid"]]],
                                         ["mstore", "_i", ["add", 1, ["mload", "_i"]]]]],
                                       ["mstore", "_i", ["add", 1, ["mload", "_i"]]]]],
                                     ["mstore8", ["add", ["add", 352, "_EXTCODESIZE"], "_op"], "_c"],
                                     ["set", "_op", ["add", "_op", 1]]]]]]]]]]]],
                           # approve the address `addr`
                           ["sstore", ["add", ["sha3_32", 0], ["mload", 320]], 1],
                           ["mstore", 0, 1],
                           ["return", 0, 32],
                           "stop"]],
                         ["if",
                          ["eq", ["mload", 0], 3258357672], # check
                          ["seq",
                           # MEMORY MAP
                           # 320: addr, the input address
                           ["calldatacopy", 320, 4, 32],
                           ["assert", ["iszero", "callvalue"]],
                           ["uclamplt", ["calldataload", 4], ["mload", 32]], # checking address input
                           ["mstore", 0, ["sload", ["add", ["sha3_32", 0], ["mload", 320]]]],
                           ["return", 0, 32],
                           "stop"]]],
                        0]]]
