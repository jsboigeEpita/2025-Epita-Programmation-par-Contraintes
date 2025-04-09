import { useState, useEffect, useRef } from 'react';
import { Settings, Play, Pause, RotateCcw, Plus, Minus, List, Target, MapPin, FastForward, Rewind } from 'lucide-react';

const RobotSimulation = () => {
  // États principaux
  const [gridSize, setGridSize] = useState({ x: 5, y: 5 });
  const [robotCount, setRobotCount] = useState(3);
  const [grid, setGrid] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showSettings, setShowSettings] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('settings');
  const [newTask, setNewTask] = useState({ x1: 0, y1: 0, x2: 0, y2: 0 });
  
  // États pour l'animation
  const [robotPaths, setRobotPaths] = useState([]);
  const [robotPositions, setRobotPositions] = useState([]);
  const [animationStep, setAnimationStep] = useState(0);
  const [maxSteps, setMaxSteps] = useState(0);
  const [animationSpeed, setAnimationSpeed] = useState(1000); // ms entre chaque pas
  const [isAnimating, setIsAnimating] = useState(false);
  const animationRef = useRef(null);
  
  // Conversion des notations en emoji
  const cellToEmoji = {
    '@': '🤖', // Robot
    'R': '📦', // Rack
    'C': '🔋', // Station de charge
    ' ': '⬜' // Cellule vide
  };

  // Effet pour gérer l'animation des robots
  useEffect(() => {
    if (isAnimating && animationStep < maxSteps) {
      animationRef.current = setTimeout(() => {
        setAnimationStep(prev => prev + 1);
      }, animationSpeed);
      
      return () => {
        if (animationRef.current) {
          clearTimeout(animationRef.current);
        }
      };
    } else if (animationStep >= maxSteps) {
      setIsAnimating(false);
    }
  }, [isAnimating, animationStep, maxSteps, animationSpeed]);

  // Effet pour mettre à jour les positions des robots à chaque étape d'animation
  useEffect(() => {
    if (robotPaths.length > 0 && animationStep <= maxSteps) {
      const newPositions = robotPaths.map(path => {
        // Si nous sommes au-delà de la longueur du chemin, utiliser la dernière position
        if (animationStep >= path.length) {
          return path[path.length - 1];
        }
        return path[animationStep];
      });
      
      setRobotPositions(newPositions);
      
      // Mettre à jour la grille avec les nouvelles positions des robots
      updateGridWithRobotPositions(newPositions);
    }
  }, [robotPaths, animationStep, maxSteps]);

  // Fonction pour mettre à jour la grille avec les positions actuelles des robots
  const updateGridWithRobotPositions = (positions) => {
    // Créer une nouvelle grille vide
    const newGrid = Array(gridSize.y).fill().map(() => Array(gridSize.x).fill(' '));
    
    // Ajouter les racks (position fixe simulée)
    const rackCount = Math.min(3, Math.floor(gridSize.x * gridSize.y * 0.1));
    const rackPositions = [];
    for (let i = 0; i < rackCount; i++) {
      const x = (i * 2) % gridSize.x;
      const y = Math.floor((i * 2) / gridSize.x) * 2;
      if (y < gridSize.y) {
        newGrid[y][x] = 'R';
        rackPositions.push({ x, y });
      }
    }
    
    // Ajouter des stations de charge (position fixe simulée)
    const chargeCount = Math.min(2, Math.floor(gridSize.x * gridSize.y * 0.05));
    const chargeStations = [];
    for (let i = 0; i < chargeCount; i++) {
      const x = (i * 3 + 1) % gridSize.x;
      const y = Math.floor((i * 3 + 1) / gridSize.x) * 3;
      if (y < gridSize.y && newGrid[y][x] === ' ') {
        newGrid[y][x] = 'C';
        chargeStations.push({ x, y });
      }
    }
    
    // Ajouter les robots à leurs positions actuelles
    // IMPORTANT: Le robot a priorité sur la station de charge pour l'affichage
    positions.forEach(pos => {
      if (pos && pos.x >= 0 && pos.x < gridSize.x && pos.y >= 0 && pos.y < gridSize.y) {
        // Même si la position est occupée par une station de charge, on met le robot
        // Les stations seront mémorisées séparément
        if (newGrid[pos.y][pos.x] !== 'R') {
          // Sauvegarder l'information si c'était une station de charge
          pos.wasChargingStation = newGrid[pos.y][pos.x] === 'C';
          // Remplacer par le robot
          newGrid[pos.y][pos.x] = '@';
        }
      }
    });
    
    setGrid(newGrid);
    
    // Conserver la liste des stations de charge pour référence
    return chargeStations;
  };

  // Simuler la récupération des données du backend
  const fetchGridFromBackend = async () => {
    try {
      // Dans une application réelle, ceci serait un appel API à votre backend Python
      console.log("Envoi des données au backend:", {
        gridSize,
        robotCount,
        tasks: tasks.map(task => ({
          xStart: task.x1,
          yStart: task.y1,
          xEnd: task.x2,
          yEnd: task.y2
        }))
      });
      
      // Simulation d'une réponse du backend
      // En réalité, vous remplaceriez ceci par un fetch() vers votre API
      
      // Simuler un délai de réseau
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simuler la création de chemins pour chaque robot
      const mockPaths = [];
      
      // Créer une grille simulée pour placer les stations de charge
      const simulatedGrid = Array(gridSize.y).fill().map(() => Array(gridSize.x).fill(' '));
      const chargeCount = Math.min(2, Math.floor(gridSize.x * gridSize.y * 0.05));
      for (let i = 0; i < chargeCount; i++) {
        const cx = (i * 3 + 1) % gridSize.x;
        const cy = Math.floor((i * 3 + 1) / gridSize.x) * 3;
        if (cy < gridSize.y) {
          simulatedGrid[cy][cx] = 'C';
        }
      }
      
      // Pour chaque robot, créer un chemin basé sur les tâches disponibles
      for (let i = 0; i < robotCount; i++) {
        // Attribuer une tâche à ce robot (simulation simplifiée)
        const task = tasks[i % tasks.length];
        
        // Créer un chemin entre le point de départ et d'arrivée
        const path = createPathBetweenPoints(
          { x: task.x1, y: task.y1 },
          { x: task.x2, y: task.y2 }
        );
        
        // Pour chaque position du chemin, vérifier si c'est une station de charge
        for (let j = 0; j < path.length; j++) {
          const pos = path[j];
          if (simulatedGrid[pos.y] && simulatedGrid[pos.y][pos.x] === 'C') {
            path[j].wasChargingStation = true;
          }
        }
        
        mockPaths.push(path);
      }
      
      // Trouver le nombre maximal d'étapes parmi tous les chemins
      const maxPathLength = Math.max(...mockPaths.map(path => path.length));
      setMaxSteps(maxPathLength);
      
      // Définir les positions initiales des robots
      const initialPositions = mockPaths.map(path => path[0]);
      setRobotPositions(initialPositions);
      
      // Mettre à jour la grille avec les positions initiales
      updateGridWithRobotPositions(initialPositions);
      
      // Stocker les chemins pour l'animation
      setRobotPaths(mockPaths);
      
      console.log("Chemins des robots générés:", mockPaths);
      
      return mockPaths;
    } catch (error) {
      console.error('Erreur lors de la récupération des données:', error);
      return [];
    }
  };

  // Créer un chemin entre deux points (algorithme simple pour la simulation)
  const createPathBetweenPoints = (start, end) => {
    const path = [{ ...start }];
    let current = { ...start };
    
    // Algorithme simple: d'abord se déplacer horizontalement, puis verticalement
    while (current.x !== end.x || current.y !== end.y) {
      // Créer un nouvel objet pour éviter les références partagées
      const next = { ...current };
      
      if (next.x < end.x) {
        next.x += 1;
      } else if (next.x > end.x) {
        next.x -= 1;
      } else if (next.y < end.y) {
        next.y += 1;
      } else if (next.y > end.y) {
        next.y -= 1;
      }
      
      // Vérifier si cette position est une station de charge dans la grille simulée
      next.wasChargingStation = checkIfPositionIsChargingStation(next.x, next.y);
      
      path.push(next);
      current = next;
    }
    
    return path;
  };
  
  // Fonction pour vérifier si une position correspond à une station de charge
  // Dans une implémentation réelle, cette information viendrait du backend
  const checkIfPositionIsChargingStation = (x, y) => {
    // Simulation simplifiée: les stations de charge sont placées à des positions spécifiques
    const chargeCount = Math.min(2, Math.floor(gridSize.x * gridSize.y * 0.05));
    for (let i = 0; i < chargeCount; i++) {
      const cx = (i * 3 + 1) % gridSize.x;
      const cy = Math.floor((i * 3 + 1) / gridSize.x) * 3;
      if (cx === x && cy === y) {
        return true;
      }
    }
    return false;
  };

  // Contrôles d'animation
  const startAnimation = () => {
    setAnimationStep(0);
    setIsAnimating(true);
  };

  const pauseAnimation = () => {
    setIsAnimating(false);
  };

  const resumeAnimation = () => {
    if (animationStep < maxSteps) {
      setIsAnimating(true);
    }
  };

  const resetAnimation = () => {
    setIsAnimating(false);
    setAnimationStep(0);
    if (robotPaths.length > 0) {
      const initialPositions = robotPaths.map(path => path[0]);
      setRobotPositions(initialPositions);
      updateGridWithRobotPositions(initialPositions);
    }
  };

  const stepForward = () => {
    if (animationStep < maxSteps) {
      setAnimationStep(prev => prev + 1);
    }
  };

  const stepBackward = () => {
    if (animationStep > 0) {
      setAnimationStep(prev => prev - 1);
    }
  };

  const changeAnimationSpeed = (faster) => {
    if (faster) {
      setAnimationSpeed(prev => Math.max(100, prev - 200));
    } else {
      setAnimationSpeed(prev => Math.min(2000, prev + 200));
    }
  };

  // Fonctions de contrôle de simulation
  const startSimulation = async () => {
    setShowSettings(false);
    setIsRunning(true);
    
    // Récupérer les données du backend et préparer l'animation
    await fetchGridFromBackend();
    
    // Démarrer automatiquement l'animation après avoir reçu les données
    setTimeout(() => {
      startAnimation();
    }, 500);
  };

  const stopSimulation = () => {
    setIsRunning(false);
    pauseAnimation();
  };

  const resetSimulation = () => {
    stopSimulation();
    setShowSettings(true);
    setGrid([]);
    setRobotPaths([]);
    setRobotPositions([]);
    setMaxSteps(0);
    setAnimationStep(0);
    setIsAnimating(false);
  };

  // Gestion des paramètres
  const incrementValue = (param) => {
    if (param === 'x') {
      setGridSize(prev => ({ ...prev, x: Math.min(prev.x + 1, 15) }));
    } else if (param === 'y') {
      setGridSize(prev => ({ ...prev, y: Math.min(prev.y + 1, 15) }));
    } else if (param === 'robots') {
      setRobotCount(prev => Math.min(prev + 1, gridSize.x * gridSize.y - 1));
    }
  };

  const decrementValue = (param) => {
    if (param === 'x') {
      setGridSize(prev => ({ ...prev, x: Math.max(prev.x - 1, 2) }));
    } else if (param === 'y') {
      setGridSize(prev => ({ ...prev, y: Math.max(prev.y - 1, 2) }));
    } else if (param === 'robots') {
      setRobotCount(prev => Math.max(prev - 1, 1));
    }
  };

  // Gestion des tâches
  const addTask = () => {
    // Validation des coordonnées par rapport à la taille de la grille
    const isValidCoord = (x, y) => x >= 0 && x < gridSize.x && y >= 0 && y < gridSize.y;
    
    if (!isValidCoord(newTask.x1, newTask.y1) || !isValidCoord(newTask.x2, newTask.y2)) {
      alert("Les coordonnées doivent être à l'intérieur de la grille");
      return;
    }
    
    const taskId = Date.now();
    setTasks([...tasks, { ...newTask, id: taskId, status: 'pending' }]);
    setNewTask({ x1: 0, y1: 0, x2: 0, y2: 0 });
  };

  const removeTask = (taskId) => {
    setTasks(tasks.filter(task => task.id !== taskId));
  };

  const changeTab = (tab) => {
    setActiveTab(tab);
  };

  const updateNewTaskField = (field, value) => {
    // Convertir la valeur en nombre et s'assurer qu'elle est dans les limites de la grille
    const numValue = parseInt(value) || 0;
    const maxVal = field.startsWith('x') ? gridSize.x - 1 : gridSize.y - 1;
    const boundedValue = Math.min(Math.max(0, numValue), maxVal);
    
    setNewTask({ ...newTask, [field]: boundedValue });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="p-6 bg-indigo-600 text-white flex justify-between items-center">
          <h1 className="text-2xl font-bold">Simulation de Robots</h1>
          {showSettings ? (
            // Onglets de configuration avant simulation
            <div className="flex space-x-1">
              <button 
                onClick={() => changeTab('settings')}
                className={`flex items-center px-3 py-2 rounded-t-lg transition-all duration-200 ${activeTab === 'settings' ? 'bg-white text-indigo-600' : 'bg-indigo-700 text-white hover:bg-indigo-800'}`}
              >
                <Settings size={18} className="mr-1" /> Paramètres
              </button>
              <button 
                onClick={() => changeTab('tasks')}
                className={`flex items-center px-3 py-2 rounded-t-lg transition-all duration-200 ${activeTab === 'tasks' ? 'bg-white text-indigo-600' : 'bg-indigo-700 text-white hover:bg-indigo-800'}`}
              >
                <List size={18} className="mr-1" /> Tâches
              </button>
            </div>
          ) : (
            // Contrôles pendant la simulation
            <div className="flex space-x-3">
              {isRunning ? (
                <button 
                  onClick={stopSimulation}
                  className="flex items-center px-3 py-2 bg-indigo-700 hover:bg-indigo-800 rounded-lg transition-all duration-200"
                >
                  <Pause size={18} className="mr-1" /> Pause
                </button>
              ) : (
                <button 
                  onClick={startSimulation}
                  className="flex items-center px-3 py-2 bg-indigo-700 hover:bg-indigo-800 rounded-lg transition-all duration-200"
                >
                  <Play size={18} className="mr-1" /> Démarrer
                </button>
              )}
              <button 
                onClick={resetSimulation}
                className="flex items-center px-3 py-2 bg-indigo-700 hover:bg-indigo-800 rounded-lg transition-all duration-200"
              >
                <RotateCcw size={18} className="mr-1" /> Réinitialiser
              </button>
            </div>
          )}
        </div>
        
        <div className="p-6">
          {showSettings ? (
            // Interface de configuration avant simulation
            <>
              {activeTab === 'settings' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                    <Settings size={20} className="mr-2 text-indigo-600" /> Paramètres de simulation
                  </h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-3">
                      <label className="block text-gray-700 font-medium">Largeur de la grille (x)</label>
                      <div className="flex items-center space-x-3">
                        <button 
                          onClick={() => decrementValue('x')}
                          className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                        >
                          <Minus size={18} />
                        </button>
                        <div className="flex-1 text-center font-bold text-lg text-indigo-700">
                          {gridSize.x}
                        </div>
                        <button 
                          onClick={() => incrementValue('x')}
                          className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                        >
                          <Plus size={18} />
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <label className="block text-gray-700 font-medium">Hauteur de la grille (y)</label>
                      <div className="flex items-center space-x-3">
                        <button 
                          onClick={() => decrementValue('y')}
                          className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                        >
                          <Minus size={18} />
                        </button>
                        <div className="flex-1 text-center font-bold text-lg text-indigo-700">
                          {gridSize.y}
                        </div>
                        <button 
                          onClick={() => incrementValue('y')}
                          className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                        >
                          <Plus size={18} />
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <label className="block text-gray-700 font-medium">Nombre de robots</label>
                      <div className="flex items-center space-x-3">
                        <button 
                          onClick={() => decrementValue('robots')}
                          className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                        >
                          <Minus size={18} />
                        </button>
                        <div className="flex-1 text-center font-bold text-lg text-indigo-700">
                          {robotCount}
                        </div>
                        <button 
                          onClick={() => incrementValue('robots')}
                          className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                        >
                          <Plus size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {activeTab === 'tasks' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                    <List size={20} className="mr-2 text-indigo-600" /> Gestion des tâches
                  </h2>
                  
                  {/* Formulaire d'ajout de tâche */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-700">Point de départ</h4>
                      <div className="flex space-x-2">
                        <div className="flex-1">
                          <label className="block text-sm text-gray-600 mb-1">X1</label>
                          <input 
                            type="number" 
                            min="0" 
                            max={gridSize.x - 1}
                            value={newTask.x1}
                            onChange={(e) => updateNewTaskField('x1', e.target.value)}
                            className="w-full p-2 border rounded-md"
                          />
                        </div>
                        <div className="flex-1">
                          <label className="block text-sm text-gray-600 mb-1">Y1</label>
                          <input 
                            type="number" 
                            min="0" 
                            max={gridSize.y - 1}
                            value={newTask.y1}
                            onChange={(e) => updateNewTaskField('y1', e.target.value)}
                            className="w-full p-2 border rounded-md"
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-700">Point d'arrivée</h4>
                      <div className="flex space-x-2">
                        <div className="flex-1">
                          <label className="block text-sm text-gray-600 mb-1">X2</label>
                          <input 
                            type="number" 
                            min="0" 
                            max={gridSize.x - 1}
                            value={newTask.x2}
                            onChange={(e) => updateNewTaskField('x2', e.target.value)}
                            className="w-full p-2 border rounded-md"
                          />
                        </div>
                        <div className="flex-1">
                          <label className="block text-sm text-gray-600 mb-1">Y2</label>
                          <input 
                            type="number" 
                            min="0" 
                            max={gridSize.y - 1}
                            value={newTask.y2}
                            onChange={(e) => updateNewTaskField('y2', e.target.value)}
                            className="w-full p-2 border rounded-md"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <button 
                    onClick={addTask}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-all duration-200"
                  >
                    Ajouter la tâche
                  </button>
                  
                  {/* Liste des tâches */}
                  {tasks.length > 0 ? (
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-700 mb-2">Tâches définies ({tasks.length})</h4>
                      <div className="border rounded-lg overflow-hidden">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Départ</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Arrivée</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {tasks.map((task) => (
                              <tr key={task.id}>
                                <td className="px-4 py-2 whitespace-nowrap">
                                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-md text-sm">
                                    ({task.x1}, {task.y1})
                                  </span>
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap">
                                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded-md text-sm">
                                    ({task.x2}, {task.y2})
                                  </span>
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap">
                                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-md text-sm">
                                    {task.status === 'pending' ? 'En attente' : task.status}
                                  </span>
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap">
                                  <button 
                                    onClick={() => removeTask(task.id)}
                                    className="px-2 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md text-sm transition-all duration-200"
                                  >
                                    Supprimer
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-4 text-center text-gray-500 py-4">
                      Aucune tâche n'a été définie
                    </div>
                  )}
                </div>
              )}
              
              {/* Bouton pour démarrer la simulation - affiché en bas peu importe l'onglet actif */}
              <div className="flex justify-center mt-8">
                <button 
                  onClick={startSimulation}
                  disabled={tasks.length === 0}
                  className={`px-6 py-3 font-medium rounded-lg transition-all duration-200 flex items-center ${
                    tasks.length === 0 
                      ? 'bg-gray-400 cursor-not-allowed text-white'
                      : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                  }`}
                >
                  <Play size={20} className="mr-2" /> Démarrer la simulation
                </button>
                {tasks.length === 0 && (
                  <div className="ml-4 text-yellow-600 flex items-center">
                    <span>Vous devez définir au moins une tâche</span>
                  </div>
                )}
              </div>
            </>
          ) : (
            // Interface de simulation
            <div className="flex flex-col items-center">
              <div className="mb-4 flex items-center space-x-6">
                <div className="flex items-center">
                  <div className="mr-2 text-xl">🤖</div>
                  <span className="text-gray-700">Robot</span>
                </div>
                <div className="flex items-center">
                  <div className="mr-2 text-xl">📦</div>
                  <span className="text-gray-700">Rack</span>
                </div>
                <div className="flex items-center">
                  <div className="mr-2 text-xl">🔋</div>
                  <span className="text-gray-700">Station de charge</span>
                </div>
              </div>
              
              {/* Contrôles d'animation */}
              <div className="mb-6 flex items-center justify-center space-x-3 bg-gray-100 p-3 rounded-lg w-full max-w-md">
                <button 
                  onClick={stepBackward}
                  className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                  disabled={animationStep === 0}
                >
                  <Rewind size={16} />
                </button>
                
                {isAnimating ? (
                  <button 
                    onClick={pauseAnimation}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all duration-200 flex items-center"
                  >
                    <Pause size={16} className="mr-1" /> Pause
                  </button>
                ) : (
                  <button 
                    onClick={resumeAnimation}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all duration-200 flex items-center"
                    disabled={animationStep >= maxSteps}
                  >
                    <Play size={16} className="mr-1" /> Lire
                  </button>
                )}
                
                <button 
                  onClick={resetAnimation}
                  className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                >
                  <RotateCcw size={16} />
                </button>
                
                <button 
                  onClick={stepForward}
                  className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-all duration-200"
                  disabled={animationStep >= maxSteps}
                >
                  <FastForward size={16} />
                </button>
                
                <div className="mx-2 text-gray-600">
                  <span className="text-sm">{animationStep}/{maxSteps}</span>
                </div>
                
                <div className="flex items-center">
                  <button 
                    onClick={() => changeAnimationSpeed(false)}
                    className="p-1 bg-gray-200 hover:bg-gray-300 rounded-l-lg transition-all duration-200"
                  >
                    <Minus size={12} />
                  </button>
                  <div className="px-2 text-xs bg-gray-200">
                    Vitesse
                  </div>
                  <button 
                    onClick={() => changeAnimationSpeed(true)}
                    className="p-1 bg-gray-200 hover:bg-gray-300 rounded-r-lg transition-all duration-200"
                  >
                    <Plus size={12} />
                  </button>
                </div>
              </div>
              
              <div className="grid gap-1 bg-gray-100 p-4 rounded-lg">
                {grid.map((row, y) => (
                  <div key={y} className="flex">
                    {row.map((cell, x) => {
                      // Vérifier si cette cellule est un point de départ ou d'arrivée d'une tâche
                      const isStartPoint = tasks.some(t => t.x1 === x && t.y1 === y);
                      const isEndPoint = tasks.some(t => t.x2 === x && t.y2 === y);
                      
                      // Vérifier si cette cellule est sur un chemin de robot (pour visualiser la trajectoire)
                      const isOnPath = robotPaths.some((path, robotIndex) => {
                        // Ne pas inclure la position actuelle du robot dans la visualisation du chemin
                        const robotPosition = robotPositions[robotIndex];
                        if (robotPosition && robotPosition.x === x && robotPosition.y === y) {
                          return false;
                        }
                        
                        // Vérifier si cette cellule est dans le chemin futur du robot (après sa position actuelle)
                        const pathPosition = path.findIndex(pos => pos.x === x && pos.y === y);
                        return pathPosition > -1 && pathPosition > path.findIndex(pos => 
                          robotPosition && pos.x === robotPosition.x && pos.y === robotPosition.y
                        );
                      });
                      
                      // Déterminer quel robot est à cette position
                      const robotIndex = robotPositions.findIndex(pos => pos && pos.x === x && pos.y === y);
                      
                      return (
                        <div 
                          key={`${x}-${y}`} 
                          className={`w-12 h-12 flex items-center justify-center border border-gray-200 rounded transition-all duration-300 relative ${
                            isOnPath ? 'bg-indigo-50' : 'bg-white'
                          } ${
                            isOnPath ? 'hover:bg-indigo-100' : 'hover:bg-indigo-50'
                          }`}
                          style={{
                            transform: cell === '@' ? 'scale(1.05)' : 'scale(1)',
                            boxShadow: cell === '@' ? '0 0 8px rgba(99, 102, 241, 0.5)' : 'none'
                          }}
                        >
                          {/* Effet spécial lorsqu'un robot est sur une station de charge - PLACÉ EN PREMIER POUR ÊTRE DERRIÈRE */}
                          {cell === '@' && 
                           robotPositions.some((pos, idx) => 
                             pos && pos.x === x && pos.y === y && pos.wasChargingStation
                           ) && (
                            <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 1 }}>
                              <div className="w-10 h-10 rounded-full bg-yellow-100 animate-pulse opacity-60"></div>
                              <div className="absolute w-8 h-8 rounded-full bg-yellow-200 animate-ping opacity-40"></div>
                              {/* Afficher l'emoji de station de charge sous le robot */}
                              <div className="text-xl opacity-40" style={{ zIndex: 2 }}>
                                🔋
                              </div>
                            </div>
                          )}
                          
                          {/* EMOJI DU ROBOT - PLACÉ APRÈS POUR ÊTRE AU-DESSUS DE L'EFFET */}
                          <div 
                            className="text-2xl relative" 
                            style={{ 
                              animation: cell === '@' ? 'pulse 2s infinite' : 'none',
                              color: cell === '@' && robotIndex > -1 ? 
                                ['#e63946', '#2a9d8f', '#f4a261', '#6d6875', '#588157'][robotIndex % 5] : 'inherit',
                              zIndex: 5 // Garantit que l'emoji est au-dessus de l'effet de charge
                            }}
                          >
                            {cellToEmoji[cell]}
                          </div>
                          
                          {/* Indicateur de point de départ */}
                          {isStartPoint && (
                            <div className="absolute top-0 left-0 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center" 
                                 title="Point de départ">
                              <MapPin size={10} className="text-white" />
                            </div>
                          )}
                          
                          {/* Indicateur de point d'arrivée */}
                          {isEndPoint && (
                            <div className="absolute top-0 right-0 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center"
                                 title="Point d'arrivée">
                              <Target size={10} className="text-white" />
                            </div>
                          )}
                          
                          {/* Coordonnées de la cellule affichées en petit */}
                          <div className="absolute bottom-0 right-1 text-xs text-gray-400">
                            {x},{y}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
              
              <div className="mt-6 text-center text-gray-600">
                <p>Nombre de robots: <span className="font-semibold">{robotCount}</span></p>
                <p>Taille de la grille: <span className="font-semibold">{gridSize.x} x {gridSize.y}</span></p>
                <p>Nombre de tâches: <span className="font-semibold">{tasks.length}</span></p>
                <p>Étape d'animation: <span className="font-semibold">{animationStep}/{maxSteps}</span></p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <style jsx>{`
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
      `}</style>
    </div>
  );
};

export default RobotSimulation;