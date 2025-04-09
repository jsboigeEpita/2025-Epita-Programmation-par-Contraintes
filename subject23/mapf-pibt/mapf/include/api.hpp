#pragma once

#include <cstddef>

extern "C"
{
    struct cPos
    {
        int x;
        int y;
    };

    struct cIdPos
    {
        int id;
        struct cPos pos;
    };

    struct cAgentInfo
    {
        int agent_id;
        struct cPos init;
        struct cPos goal;
    };

    struct cIdPos* next_step(struct cAgentInfo* agent_info_arg, size_t size,
                             char* path);
}
