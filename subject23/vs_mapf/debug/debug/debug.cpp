<<<<<<< HEAD
// debug.cpp : Ce fichier contient la fonction 'main'. L'exécution du programme commence et se termine à cet endroit.
//

#include <iostream>
#include "api.hpp"

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

int main()
{
    std::cout << "Hello World!\n";

    struct cPos a {0,0};
    struct cPos b {2,2};

    struct cAgentInfo c {0, a, b};

    std::cout << c.agent_id << "\n";
    std::cout << c.goal.x << "," << c.goal.y << "\n";
    std::cout << c.init.x << "," << c.init.y << "\n\n";

    struct cIdPos* result = next_step_wrapper(&c, 1, (char *)"C:\\Users\\Julien\\AppData\\LocalLow\\DefaultCompany\\MultiBotWarehouse\\map.ssv");

    std::cout << result->id << "\n";
    std::cout << result->pos.x << "," << result->pos.y << "\n\n\n";

    for (size_t i = 0; i < 10; i++)
    {
        c = { 0, result->pos, b };

        std::cout << c.agent_id << "\n";
        std::cout << c.goal.x << "," << c.goal.y << "\n";
        std::cout << c.init.x << "," << c.init.y << "\n\n";

        result = next_step_wrapper(&c, 1, (char*)"C:\\Users\\Julien\\AppData\\LocalLow\\DefaultCompany\\MultiBotWarehouse\\map.ssv");

        std::cout << result->id << "\n";
        std::cout << result->pos.x << "," << result->pos.y << "\n";
    }
}

// Exécuter le programme : Ctrl+F5 ou menu Déboguer > Exécuter sans débogage
// Déboguer le programme : F5 ou menu Déboguer > Démarrer le débogage

// Astuces pour bien démarrer : 
//   1. Utilisez la fenêtre Explorateur de solutions pour ajouter des fichiers et les gérer.
//   2. Utilisez la fenêtre Team Explorer pour vous connecter au contrôle de code source.
//   3. Utilisez la fenêtre Sortie pour voir la sortie de la génération et d'autres messages.
//   4. Utilisez la fenêtre Liste d'erreurs pour voir les erreurs.
//   5. Accédez à Projet > Ajouter un nouvel élément pour créer des fichiers de code, ou à Projet > Ajouter un élément existant pour ajouter des fichiers de code existants au projet.
//   6. Pour rouvrir ce projet plus tard, accédez à Fichier > Ouvrir > Projet et sélectionnez le fichier .sln.
=======
// debug.cpp : Ce fichier contient la fonction 'main'. L'exécution du programme commence et se termine à cet endroit.
//

#include <iostream>
#include "api.hpp"

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

int main()
{
    std::cout << "Hello World!\n";

    struct cPos a {0,0};
    struct cPos b {2,2};

    struct cAgentInfo c {0, a, b};

    std::cout << c.agent_id << "\n";
    std::cout << c.goal.x << "," << c.goal.y << "\n";
    std::cout << c.init.x << "," << c.init.y << "\n\n";

    struct cIdPos* result = next_step_wrapper(&c, 1, (char *)"C:\\Users\\Julien\\AppData\\LocalLow\\DefaultCompany\\MultiBotWarehouse\\map.ssv");

    std::cout << result->id << "\n";
    std::cout << result->pos.x << "," << result->pos.y << "\n\n\n";

    for (size_t i = 0; i < 10; i++)
    {
        c = { 0, result->pos, b };

        std::cout << c.agent_id << "\n";
        std::cout << c.goal.x << "," << c.goal.y << "\n";
        std::cout << c.init.x << "," << c.init.y << "\n\n";

        result = next_step_wrapper(&c, 1, (char*)"C:\\Users\\Julien\\AppData\\LocalLow\\DefaultCompany\\MultiBotWarehouse\\map.ssv");

        std::cout << result->id << "\n";
        std::cout << result->pos.x << "," << result->pos.y << "\n";
    }
}

// Exécuter le programme : Ctrl+F5 ou menu Déboguer > Exécuter sans débogage
// Déboguer le programme : F5 ou menu Déboguer > Démarrer le débogage

// Astuces pour bien démarrer : 
//   1. Utilisez la fenêtre Explorateur de solutions pour ajouter des fichiers et les gérer.
//   2. Utilisez la fenêtre Team Explorer pour vous connecter au contrôle de code source.
//   3. Utilisez la fenêtre Sortie pour voir la sortie de la génération et d'autres messages.
//   4. Utilisez la fenêtre Liste d'erreurs pour voir les erreurs.
//   5. Accédez à Projet > Ajouter un nouvel élément pour créer des fichiers de code, ou à Projet > Ajouter un élément existant pour ajouter des fichiers de code existants au projet.
//   6. Pour rouvrir ce projet plus tard, accédez à Fichier > Ouvrir > Projet et sélectionnez le fichier .sln.
>>>>>>> 7b751068716c32c3e20fe29aea2ece2af8df54b7
