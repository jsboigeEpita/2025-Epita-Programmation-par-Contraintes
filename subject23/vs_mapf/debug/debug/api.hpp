#pragma once

#include <cstddef>
#include <cstdlib>

extern "C"
{
    __declspec(dllimport) struct cIdPos*
        next_step_wrapper(struct cAgentInfo* agent_info_arg, size_t size,
            char* path);

    __declspec(dllimport) void free_cIdPos(struct cIdPos* arr);
}
