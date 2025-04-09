#pragma once

#include <map>

#include "node.hpp"
#include "pos.hpp"
#include "problem.hpp"
#include "solver.hpp"
class Pibt_api : public Solver
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
    struct AgentInfo
    {
        int id;
        Node* init;
        Node* goal;
    };
    using AgentsInfo = std::vector<struct AgentInfo*>;
    std::map<int, Agent> current_agents_{}; // to save the current state of each

    std::vector<std::tuple<int, Pos>> get_next_step(AgentsInfo& agents_info);

public:
    Pibt_api(Problem* _P);
    ~Pibt_api()
    {}
};
