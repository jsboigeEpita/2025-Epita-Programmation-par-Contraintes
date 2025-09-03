#include "../include/api.hpp"

#include <string>

#include "../include/pibt_api.hpp"

struct cIdPos* next_step(struct cAgentInfo* agent_info_arg, size_t size,
                         char* path)
{
    std::string instance_file{ path };
    std::vector<AgentInfo> agent_info{};
    for (size_t i = 0; i < size; i++)
    {
        agent_info.push_back(
            AgentInfo{ agent_info_arg[i].agent_id,
                       Pibt_api::instance(instance_file).getNode(agent_info_arg[i].init.x,
                                        agent_info_arg[i].init.y),
                       Pibt_api::instance(instance_file).getNode(agent_info_arg[i].goal.x,
                                        agent_info_arg[i].goal.y) });
    }
    std::vector<cIdPos> next_steps = Pibt_api::instance(instance_file).get_next_step(agent_info);

    void* raw_memory = operator new[](next_steps.size() * sizeof(cIdPos));
    cIdPos* id_pos_arr = static_cast<cIdPos*>(raw_memory);

    for (size_t i = 0; i < next_steps.size(); i++)
    {
        id_pos_arr[i] = next_steps[i];
    }

    return id_pos_arr;
}
