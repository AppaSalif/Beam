import os
import sys

# Add the python package to the path
sys.path.insert(0, os.path.expanduser('~/sofa/plugins/Cosserat/python'))

from cosserat import BeamGeometryParameters, CosseratGeometry


stiffness_param: float = 1e10
v_damping_param: float = 1. #3e-1  # Damping parameter for dynamics
beam_mass: float = 0.5
nb_section: int = 7
beam_length: float = 5
beam_radius: float = 0.3
youngModulus: float = 1e3
poissonRatio: float = 0.38

def createScene(root):
    """Create a Cosserat beam scene with forces and dynamics."""
    # Configure scene with time integration
    root.addObject("RequiredPlugin", pluginName="Sofa.Component.Mass")
    root.addObject("RequiredPlugin", pluginName="Sofa.Component.SolidMechanics.Spring")
    root.addObject("RequiredPlugin", pluginName="Sofa.Component.StateContainer")
    root.addObject("RequiredPlugin", pluginName="Sofa.Component.Visual")
    root.addObject("RequiredPlugin", pluginName="Cosserat")
    root.addObject('RequiredPlugin', pluginName='Sofa.Component.LinearSolver.Direct') # Needed to use components [SparseLDLSolver]  
    root.addObject('RequiredPlugin', pluginName='Sofa.Component.ODESolver.Backward') # Needed to use components [EulerImplicitSolver]  
    root.addObject('RequiredPlugin', pluginName='Sofa.Component.LinearSolver.Iterative') # Needed to use components [CGLinearSolver]  
    root.addObject('RequiredPlugin', pluginName='Sofa.Component.Constraint.Projective') # Needed to use components [FixedProjectiveConstraint]
    root.addObject("RequiredPlugin", pluginName="SofaValidation")

    # Configure scene
    root.addObject(
        "VisualStyle",
        displayFlags="showBehaviorModels showCollisionModels showMechanicalMappings",
    )
    root.addObject("DefaultAnimationLoop")

    # Add gravity
    root.gravity = [0, -9.81, 0]  # Add gravity!
    root.dt = 1e-3

    # Configure time integration and solver

    ## solver node
    solver = root.addChild("solver_node")
    solver.addObject("EulerImplicitSolver", 
                     firstOrder="0", 
                     rayleighMass=0, 
                     rayleighStiffness=0, 
                     vdamping=v_damping_param
                     )
    
    solver.addObject("CGLinearSolver", iterations=1000, tolerance=1e-12, threshold=1e-12)

    beam_geometry_params = BeamGeometryParameters(
        beam_length=beam_length,
        nb_section=nb_section,
        nb_frames=nb_section,
    )    
        
    beam_geometry = CosseratGeometry(beam_geometry_params)

    # On génère la liste des indices que l'on veut monitorer (0, 1, 2... 10)
    indices_str = "   ".join([str(i) for i in range(nb_section)])

    ## base node
    rigid_base = solver.addChild("rigid_base")
    rigid_base.addObject(
        "MechanicalObject",
        template="Rigid3d",
        name="cosserat_base_mo",
        position=[0, 0, 0, 0, 0, 0, 1],
        showObject=True,
        showObjectScale="0.1",
    )
    rigid_base.addObject(
        "RestShapeSpringsForceField",
        name="spring",
        stiffness=stiffness_param,
        angularStiffness=stiffness_param,
        external_points="0",
        mstate="@cosserat_base_mo",
        points="0",
        template="Rigid3d",
    )
    
    ## frame node
    frame_node = solver.addChild("frame_node")
    frames_mo = frame_node.addObject(
        "MechanicalObject",
        template="Rigid3d",
        name="FramesMO",
        position=beam_geometry.frames,  # Use geometry data
        showIndices=1,
        showObject=1,
        showObjectScale=0.8,
    )
    frame_node.addObject("FixedProjectiveConstraint", indices="0")
    
    frame_node.addObject("UniformMass", totalMass=beam_mass)

    ## bending node
    custom_bending_states = [[0, 0, 0, 1, 0, 0] for _ in range(nb_section)]
    strain_node = frame_node.addChild("strain_node")

    strain_node.addObject(
        "MechanicalObject",
        template="Vec6d",
        name="cosserat_state",
        position=custom_bending_states,
    )
    strain_node.addObject(
        "BeamHookeLawForceField",
        crossSectionShape="circular",
        length=beam_geometry.section_lengths,  # Use geometry data
        radius=beam_radius,
        youngModulus=youngModulus,
        poissonRatio=poissonRatio,
    )

    strain_node.addObject(
    "Frames2StrainCosseratMapping", 
    curv_abs_input=beam_geometry.curv_abs_sections, 
    curv_abs_output=beam_geometry.curv_abs_frames, 
    name="cosseratMapping",
    input1=frame_node.getLinkPath(), 
    input2=rigid_base.cosserat_base_mo.getLinkPath(), 
    output=strain_node.cosserat_state.getLinkPath(), 
    debug=0,
    radius=beam_radius, 
    color=[0., 1., 0., 0.5], #green   
    )


    frame_node.addObject("Monitor", name="Monitor_Frames2Strain", template="Rigid3d", 
                           listening=True, indices=indices_str, showPositions=True, 
                           ExportPositions=True, ExportVelocities=False, 
                           ExportForces=False, fileName="monitor_frames2strain")
    

    return root
