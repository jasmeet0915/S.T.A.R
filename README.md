# S.T.A.R
Satellite Trajectory Animation Renderer: Satellite Orbit Visualiser using Blender 
<br><br>
<img src = "https://user-images.githubusercontent.com/23265149/83307886-3ed62c80-a223-11ea-8d5c-7f2c48bbf43b.png" width="600"/>

This project shows how you can create cool looking yet 'Scientifically Correct Orbital Simulations' for any satellite you want
using Blender and Python.

<h2>Two Line Element(TLE) Set</h2>
Orbit Prediction for any Earth-orbiting object is done using the Classical/Keplerian Orbital Elements. The orbital elements 
associated with an Earth-orbiting object generally comprise of six elements which describes the shape, size and orientation 
of its orbit. 

A generalized data format known as the <b>Two Line Element (TLE)</b> Set is used to keep track of the orbital elements of 
individual satellites and are used by Organizations to keep track of the satellites and debris in space. TLE data for any satellite can be taken from <a href="https://celestrak.com/NORAD/elements/">this website</a>.

<h2>How it Works</h2>
<ol>
  <li>Create a model of the Earth in a new blender file using a UV sphere and applying the given texture to it. If you want to make the Holographic Earth shown above, <a href="https://www.youtube.com/watch?v=doNVizFGGVQ">follow this video</a>.<br>
    
  <li>Animate the rotation of the earth model to rotate about the z axis 360 degrees in 2 mins using keyframes.<br>
    
  <li>Create a satellite model, which in this case was just another UV sphere with emission shader applied to it. Then create a particle system which refers to the satellite object with the following settings:<br>
    <ol>
      <li>Set the number of the particles equal to the number of satellites.<br>
      <li>Set gravity equal to 0 and change the lifetime to span across the complete animation. This ensures all the particles stay in the frame.<br>
      <li>Check the disk cache option in the cache section of the Particles and Bake the simulation to get the particle cache files saved in your project folder. These particle cache files will be later overwritten with the satellite location data.<br>
    </ol>
   <li>Copy the Starlink satellite TLE data from <a href="https://celestrak.com/NORAD/elements/starlink.txt">this link</a>.<br>
     
   <li>Save the data in a "starlink.txt" file inside the data directory of the orbital_mechanics and execute the <code>main.py</code> file.<br>
     
   <li>This file extracts all the required orbital elements from the TLE data and passes it to <code>OrbitPropagator.py</code> which calculates the state vectors(position and velocity) for that satelliet at every timestep <code>dt</code>.<br>
     
  <li>The <code>OrbitPropagator.py</code> script makes use of the Ordinary Differential Equation Solver from the scipy module and applies it to the differential equation obtained by considering a 2 Body Gravitational Inetraction between the Earth and the Satellite.
  <img src= "https://user-images.githubusercontent.com/23265149/83329701-a4203100-a2a8-11ea-8241-e7e07b04a1e8.png" width="600"/>
  <br><br>
  <li>The location data for each satellite for every timestep is stored in a list and then written to the blender's particle cache files for every frame using the <code>particlecahce.py</code> script.<br>
  
   <li>Now when you run the animation in blender it will animate the particles according to the location data written in the particle cache files by orbital_mechanics. 
</ol>
