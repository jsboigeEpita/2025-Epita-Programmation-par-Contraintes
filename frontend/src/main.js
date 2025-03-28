import * as THREE from 'three';
import { OrbitControls } from 'three/examples/js/controls/OrbitControls';

// Créer la scène
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Créer la Terre
const geometry = new THREE.SphereGeometry(1, 32, 32);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const earth = new THREE.Mesh(geometry, material);
scene.add(earth);

// Placer la caméra
camera.position.z = 5;

// Initialiser les contrôles d'orbite
const controls = new OrbitControls(camera, renderer.domElement);

// Fonction de rendu
function animate() {
    requestAnimationFrame(animate);

    // Animation du satellite
    earth.rotation.y += 0.01;

    controls.update();

    renderer.render(scene, camera);
}

animate();

// Récupérer les données du backend pour la mission satellite
fetch('/mission_plan')
  .then(response => response.json())
  .then(data => {
    console.log(data);  // Afficher les données de la mission
  })
  .catch(error => {
    console.error('Erreur:', error);
  });
