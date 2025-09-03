#pragma once

#include <cstddef>
#include <cstdlib>

struct cIdPos* next_step(struct cAgentInfo* agent_info_arg, size_t size,
                         char* path);

// extern "C"
// {
//     /*  __declspec(dllexport) */
//     struct cIdPos* next_step_wrapper(struct cAgentInfo* agent_info_arg,
//     size_t size,
//                       char* path)
//     {
//         return next_step(agent_info_arg, size, path);
//     }
//
//     // __declspec(dllexport) void free_cIdPos(struct cIdPos* arr)
//     // {
//     //     free(arr);
//     // }
//
//     // __declspec(dllexport) int test(int i)
//     // {
//     //     return i + 21;
//     // }
// }
