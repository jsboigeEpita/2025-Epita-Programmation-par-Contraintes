#pragma once

#include <map>

#include "node.hpp"
#include "problem.hpp"
#include "singleton.hh"
#include "solver.hpp"
#include "struct_api.hpp"

struct AgentInfo
{
    int id;
    Node* init;
    Node* goal;
};

class Pibt_api
    : public Solver
    , public Singleton<Pibt_api>
{
private:
    // PIBT agent
    struct Agent
    {
        int id;
        Node* v_now; // current location
        Node* v_next; // next location
        Node* g; // goal
        int elapsed; // eta
        int init_d; // initial distance
        float tie_breaker; // epsilon, tie-breaker
    };
    using Agents = std::vector<Agent*>;

    // <node-id, agent>, whether the node is occupied or not
    // work as reservation table
    Agents occupied_now;
    Agents occupied_next;

    // option
    bool disable_dist_init = false;

    // result of priority inheritance: true -> valid, false -> invalid
    bool funcPIBT(Agent* ai);
    // plan next node
    Node* planOneStep(Agent* a);
    // chose one node from candidates, used in planOneStep
    Node* chooseNode(Agent* a);

    // main
    // void run();
    using AgentsInfo = std::vector<struct AgentInfo>;
    std::map<int, Agent> current_agents_{}; // to save the current state of each

public:
    Node* getNode(int x, int y)
    {
        return G->getNode(x, y);
    }
    std::vector<cIdPos> get_next_step(AgentsInfo& agents_info);

    static Pibt_api& instance(const std::string& instance_file) {
        static Pibt_api inst(instance_file);
        return inst;
    }

private:
    Pibt_api(std::string instance_file)
            : Pibt_api{ new Problem(instance_file)} {
    };

    ~Pibt_api() {
        delete P;
    }

    Pibt_api(Problem* _P);

    // pour empêcher la copie
    Pibt_api(const Pibt_api&) = delete;
    Pibt_api& operator=(const Pibt_api&) = delete;

};
