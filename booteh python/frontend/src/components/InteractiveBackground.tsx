import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const InteractiveBackground = () => {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) {
      return undefined;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 0.1, 1000);
    camera.position.z = 32;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    mount.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0x88aaff, 0.4);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x6f8cff, 1.2);
    pointLight.position.set(16, 18, 12);
    scene.add(pointLight);

    const gradientMaterial = new THREE.ShaderMaterial({
      uniforms: {
        color1: { value: new THREE.Color(0x2b1742) },
        color2: { value: new THREE.Color(0x3b3f75) }
      },
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: `varying vec2 vUv; uniform vec3 color1; uniform vec3 color2; void main(){ gl_FragColor = vec4(mix(color1, color2, vUv.y), 0.85); }`,
      transparent: true,
      side: THREE.BackSide
    });

    const backdropGeometry = new THREE.SphereGeometry(80, 32, 32);
    const backdrop = new THREE.Mesh(backdropGeometry, gradientMaterial);
    scene.add(backdrop);

    const shapes: THREE.Mesh[] = [];
    const palette = [0x38bdf8, 0x7c3aed, 0x67e8f9, 0xf472b6];
    const createShape = (geometry: THREE.BufferGeometry, index: number) => {
      const material = new THREE.MeshStandardMaterial({
        color: palette[index % palette.length],
        emissive: palette[index % palette.length],
        emissiveIntensity: 0.25,
        metalness: 0.6,
        roughness: 0.25,
        transparent: true,
        opacity: 0.88
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set((Math.random() - 0.5) * 32, (Math.random() - 0.5) * 18, (Math.random() - 0.5) * 18);
      mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
      const scale = 1.8 + Math.random() * 2.5;
      mesh.scale.set(scale, scale, scale);
      mesh.userData.baseScale = scale;
      scene.add(mesh);
      shapes.push(mesh);
    };

    const geometries = [
      new THREE.IcosahedronGeometry(2.5, 0),
      new THREE.TorusKnotGeometry(2, 0.6, 120, 32),
      new THREE.OctahedronGeometry(2.2, 0)
    ];

    for (let i = 0; i < 18; i += 1) {
      createShape(geometries[i % geometries.length], i);
    }

    const particleGeometry = new THREE.BufferGeometry();
    const particleCount = 420;
    const positions = new Float32Array(particleCount * 3);
    const velocities: number[] = [];

    for (let i = 0; i < particleCount; i += 1) {
      positions[i * 3] = (Math.random() - 0.5) * 80;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 40;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 60;
      velocities.push((Math.random() - 0.5) * 0.02);
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.45,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending
    });
    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();

    const onPointerMove = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    };

    renderer.domElement.addEventListener('pointermove', onPointerMove);

    let frameId: number;

    const animate = () => {
      frameId = requestAnimationFrame(animate);

      raycaster.setFromCamera(pointer, camera);
      const intersects = raycaster.intersectObjects(shapes, false);
      shapes.forEach((shape, index) => {
        shape.rotation.x += 0.003 + (index % 5) * 0.0006;
        shape.rotation.y += 0.0025 + (index % 3) * 0.0005;
        const hover = intersects.find((item) => item.object === shape);
        const baseScale = shape.userData.baseScale as number;
        const targetScale = hover ? baseScale * 1.2 : baseScale;
        shape.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.08);
      });

      const positionsAttribute = particleGeometry.getAttribute('position') as THREE.BufferAttribute;
      for (let i = 0; i < positionsAttribute.count; i += 1) {
        const y = positionsAttribute.getY(i) + velocities[i];
        positionsAttribute.setY(i, y > 20 ? -20 : y < -20 ? 20 : y);
      }
      positionsAttribute.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!mount) return;
      const { clientWidth, clientHeight } = mount;
      camera.aspect = clientWidth / clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(clientWidth, clientHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('pointermove', onPointerMove);
      if (renderer.domElement.parentElement === mount) {
        mount.removeChild(renderer.domElement);
      }
      renderer.dispose();
      gradientMaterial.dispose();
      particleMaterial.dispose();
      particleGeometry.dispose();
      backdropGeometry.dispose();
      geometries.forEach((geometry) => geometry.dispose());
      shapes.forEach((shape) => {
        shape.geometry.dispose();
        if (Array.isArray(shape.material)) {
          shape.material.forEach((material) => material.dispose());
        } else {
          shape.material.dispose();
        }
      });
    };
  }, []);

  return <div ref={mountRef} style={{ position: 'absolute', inset: 0, zIndex: 0 }} />;
};

export default InteractiveBackground;
