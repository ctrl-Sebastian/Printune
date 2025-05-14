"""
modeling.py - Handles 3D model generation and export for Tagify.
"""

import cadquery as cq

def generate_model_without_export(bar_heights, selected_base_model):
    """
    Generate the model in memory without exporting it.
    Returns a CadQuery Workplane object.
    """
    if not bar_heights or not selected_base_model:
        return None
    try:
        model = cq.importers.importStep(selected_base_model)
        curr_bar = 0
        for bar in bar_heights:
            model = (
                model.pushPoints([(15.5 + curr_bar * 1.88, 7.5)])
                .sketch()
                .slot(9 / 5 * bar, 1, 90)
                .finalize()
                .extrude(4)
            )
            curr_bar += 1
        return model
    except Exception as e:
        print(f"Error generating model: {e}")
        return None

def export_model(model, file_path):
    """
    Export the given CadQuery model to an STL file.
    """
    cq.exporters.export(model, file_path, exportType='STL')
