#pragma once

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
