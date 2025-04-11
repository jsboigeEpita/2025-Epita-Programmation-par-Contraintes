#include "../include/pibt_api.hpp"

#include <queue>

Pibt_api::Pibt_api(Problem* _P)
    : Solver(_P)
    , occupied_now(Agents(G->getNodesSize(), nullptr))
    , occupied_next(Agents(G->getNodesSize(), nullptr))
{}

std::vector<cIdPos> Pibt_api::get_next_step(AgentsInfo& agents_info)
{
    P->clear();
    occupied_now.clear();
    occupied_next.clear();
    occupied_now.resize(G->getNodesSize(), nullptr);
    occupied_next.resize(G->getNodesSize(), nullptr);

    // compare priority of agents
    auto compare = [](Agent* a, const Agent* b) {
        if (a->elapsed != b->elapsed)
            return a->elapsed < b->elapsed;
        // use initial distance
        if (a->init_d != b->init_d)
            return a->init_d < b->init_d;
        return a->tie_breaker < b->tie_breaker;
    };

    // agents have not decided their next locations
    std::priority_queue<Agent*, Agents, decltype(compare)> undecided(compare);
    // agents have already decided their next locations
    std::vector<Agent*> decided;

    // initialize problem
    for (int i = 0; i < agents_info.size(); ++i)
    {
        Node* s = agents_info[i].init;
        Node* g = agents_info[i].goal;
        Agent* a = nullptr;
        auto agent = current_agents_.find(agents_info[i].id);
        if (agent != current_agents_.end())
        {
            a = &agent->second;
            a->v_now = agents_info[i].init;
            a->v_next = nullptr;

            undecided.push(a);
            occupied_now[s->id] = a;
            P->setStart(a->id, s);
            P->setGoal(a->id, g);
            if (a->g != agents_info[i].goal) {
                // rework
                a->g = agents_info[i].goal;
                this->createDistanceTable(a->id);
            }
        }
        else
        {
            int d = 0;
            a = new Agent{ i, // id
                           s, // current location
                           nullptr, // next location
                           g, // goal
                           0, // elapsed
                           d, // dist from s -> g
                           getRandomFloat(0, 1, MT) }; // tie-breaker
            current_agents_.insert({ a->id, *a });

            undecided.push(a);
            occupied_now[s->id] = a;
            P->setStart(a->id, s);
            P->setGoal(a->id, g);
            this->createDistanceTable(a->id);
        }
    }
    // planning
    while (!undecided.empty())
    {
        // pickup the agent with highest priority
        Agent* a = undecided.top();
        undecided.pop();

        // if the agent has next location, then skip
        if (a->v_next == nullptr)
        {
            // determine its next location
            funcPIBT(a);
        }
        decided.push_back(a);
    }
    // now all next location are in agent
    std::vector<cIdPos> res{};
    for (const auto agent : decided)
    {
        res.push_back(cIdPos{ agent->id,
                              { agent->v_next->pos.x, agent->v_next->pos.y } });
    }
    // acting
    for (auto a : decided) {
      // update priority
      a->elapsed = (a->v_next == a->g) ? 0 : a->elapsed + 1;
      // reset params
      a->v_now = a->v_next;
      a->v_next = nullptr;
    }
    return res;
}

bool Pibt_api::funcPIBT(Agent* ai)
{
    // decide next node
    Node* v = planOneStep(ai);
    while (v != nullptr)
    {
        auto aj = occupied_now[v->id];
        if (aj != nullptr)
        { // someone occupies v
            // avoid itself && allow rotations
            if (aj != ai && aj->v_next == nullptr)
            {
                // do priority inheritance and backtracking
                if (!funcPIBT(aj))
                {
                    // replan
                    v = planOneStep(ai);
                    continue;
                }
            }
        }
        // success to plan next one step
        return true;
    }
    // failed to secure node, cope stuck
    occupied_next[ai->v_now->id] = ai;
    ai->v_next = ai->v_now;
    return false;
}

/*
 * no candidate node -> return nullptr
 */
Node* Pibt_api::planOneStep(Agent* a)
{
    Node* v = chooseNode(a);
    if (v != nullptr)
    {
        // update reservation
        occupied_next[v->id] = a;
        a->v_next = v;
    }
    return v;
}

// no candidate node -> return nullptr
Node* Pibt_api::chooseNode(Agent* a)
{
    // candidates
    Nodes C = a->v_now->neighbor;
    C.push_back(a->v_now);

    // randomize
    std::shuffle(C.begin(), C.end(), *MT);

    // desired node
    Node* v = nullptr;

    // pickup one node
    for (auto u : C)
    {
        // avoid vertex conflict
        if (occupied_next[u->id] != nullptr)
            continue;
        // avoid swap conflict
        auto a_j = occupied_now[u->id];
        if (a_j != nullptr && a_j->v_next == a->v_now)
            continue;

        // goal exists -> return immediately
        if (u == a->g)
            return u;

        // determine the next node
        if (v == nullptr)
        {
            v = u;
        }
        else
        {
            int c_v = pathDist(a->id, v);
            int c_u = pathDist(a->id, u);
            if ((c_u < c_v)
                || (c_u == c_v && occupied_now[v->id] != nullptr
                    && occupied_now[u->id] == nullptr))
            {
                v = u;
            }
        }
    }

    return v;
}
