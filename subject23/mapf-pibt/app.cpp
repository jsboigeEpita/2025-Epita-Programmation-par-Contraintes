
#include <iostream>

#include "mapf/include/api.hpp"
#include "mapf/include/struct_api.hpp"

int main(int argc, char* argv[])
{
    struct cPos init{ 0, 0 };
    struct cPos goal{ 0, 3 };

    struct cAgentInfo agent0{ 0, init, goal };
    char instance_path[] = "/home/lois/Groupe23-Programmation-par-Contraintes/"
                           "subject23/mapf-pibt/instances/instance.txt";

    int i = 0;
    struct cIdPos res;
    do {
        if (i == 20) {
            agent0.goal= {4, 5};
        }
        res = next_step(&agent0, 1, instance_path)[0];
        std::cout << res.pos.x << ", " << res.pos.y << std::endl;
        agent0.init.x = res.pos.x;
        agent0.init.y = res.pos.y;

    } while (++i < 30);
}