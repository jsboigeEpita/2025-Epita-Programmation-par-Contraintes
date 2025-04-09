import { useState, useEffect } from 'react';
import { Settings, Play, Pause, RotateCcw, Plus, Minus, List, Target, MapPin } from 'lucide-react';

const RobotSimulation = () => {
  // États
  const [gridSize, setGridSize] = useState({ x: 5, y: 5 });
  const [robotCount, setRobotCount] = useState(3);
  const [grid, setGrid] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showSettings, setShowSettings] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('settings'); // 'settings' ou 'tasks'
  const [newTask, setNewTask] = useState({ x1: 0, y1: 0, x2: 0, y2: 0 });

  // Conversion des notations en emoji
  const cellToEmoji = {
    '@': '🤖', // Robot
    'R': '📦', // Rack
    'C': '🔋', // Station de charge
    ' ': '⬜' // Cellule vide
  };

  // Simuler la récupération des données du backend
  useEffect(() => {
    if (isRunning) {
      fetchGridFromBackend();
      const interval = setInterval(fetchGridFromBackend, 1500);
      return () => clearInterval(interval);
    }
  }, [isRunning, gridSize, robotCount]);

  // Fonctions de manipulation du backend
  const fetchGridFromBackend = () => {
    // Simulation d'une réponse du backend
    // Dans une application réelle, ceci serait un appel API à votre backend Python
    const mockGrid = generateMockGrid(gridSize.x, gridSize.y, robotCount);
    setGrid(mockGrid);
  };

  const generateMockGrid = (x, y, robots) => {
    const newGrid = Array(y).fill().map(() => Array(x).fill(' '));
    
    // Ajouter des racks (entre 2 et 5)
    const rackCount = Math.floor(Math.random() * 4) + 2;
    for (let i = 0; i < rackCount; i++) {
      const rx = Math.floor(Math.random() * x);
      const ry = Math.floor(Math.random() * y);
      if (newGrid[ry][rx] === ' ') newGrid[ry][rx] = 'R';
    }
    
    // Ajouter des stations de charge (entre 1 et 3)
    const chargeCount = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < chargeCount; i++) {
      const cx = Math.floor(Math.random() * x);
      const cy = Math.floor(Math.random() * y);
      if (newGrid[cy][cx] === ' ') newGrid[cy][cx] = 'C';
    }
    
    // Ajouter des robots
    for (let i = 0; i < robots; i++) {
      const rx = Math.floor(Math.random() * x);
      const ry = Math.floor(Math.random() * y);
      if (newGrid[ry][rx] === ' ') newGrid[ry][rx] = '@';
    }
    
    return newGrid;
  };

  // Fonctions de contrôle de simulation
  const startSimulation = () => {
    setShowSettings(false);
    setIsRunning(true);
  };

  const stopSimulation = () => {
    setIsRunning(false);
  };

  const resetSimulation = () => {
    stopSimulation();
    setShowSettings(true);
    setGrid([]);
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
              
              <div className="grid gap-1 bg-gray-100 p-4 rounded-lg">
                {grid.map((row, y) => (
                  <div key={y} className="flex">
                    {row.map((cell, x) => {
                      // Vérifier si cette cellule est un point de départ ou d'arrivée d'une tâche
                      const isStartPoint = tasks.some(t => t.x1 === x && t.y1 === y);
                      const isEndPoint = tasks.some(t => t.x2 === x && t.y2 === y);
                      
                      return (
                        <div 
                          key={`${x}-${y}`} 
                          className="w-12 h-12 flex items-center justify-center border border-gray-200 bg-white rounded transition-all duration-300 hover:bg-indigo-50 relative"
                          style={{
                            transform: cell === '@' ? 'scale(1.05)' : 'scale(1)',
                            boxShadow: cell === '@' ? '0 0 8px rgba(99, 102, 241, 0.5)' : 'none'
                          }}
                        >
                          <div className="text-2xl" style={{ animation: cell === '@' ? 'pulse 2s infinite' : 'none' }}>
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