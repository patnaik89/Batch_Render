# generates commands to batch render via the command line

import maya.cmds as cmds
import maya.mel as mel
import os.path

def UI():
    """generates the UI window"""
    # check to see if window exists
    if (cmds.window('batch', exists=True)):
        cmds.deleteUI('batch')

    # create window
    window = cmds.window('batch', title='Batch Render Commands', w=640, h=480, mxb=True, mnb=True, sizeable=True)
    
    # create layout
    main_layout = cmds.columnLayout(w=640, h=480)
    
    # get the current render layer
    curr_layer = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)
    
    # select render directory
    cmds.separator(h=15)
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(160, 320, 160))
    cmds.text(label='Render Directory', w=145, al='right')
    image_directory = cmds.workspace(q=True, rd=True)
    image_directory = os.path.join(image_directory, 'images', '')
    cmds.textField('render_dir_field', w=320, tx=image_directory)
    cmds.button(label='Select Render Directory', w=160, command=sel_render_dir)
    cmds.setParent('..')
    
    # define folder name
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 320))
    cmds.text(label='Name', w=145, al='right')
    cmds.textField('name', w=320, tx=curr_layer)
    cmds.setParent('..')
    
    # select renderer
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 320))
    cmds.text(label='Renderer', w=145, al='right')
    cmds.optionMenu('renderer')
    cmds.menuItem(label='mr', parent='renderer')
    cmds.setParent('..')
    
    # select render layer
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 320))
    cmds.text(label='Render Layer', w=145, al='right')
    cmds.optionMenu('rl', changeCommand=update_name)
    populate_option('renderLayer', 'rl')
    select_current('rl', 'renderLayer', curr_layer)
    cmds.setParent('..')
    
    # select camera
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 320))
    cmds.text(label='Camera', w=145, al='right')
    cmds.optionMenu('cam')
    populate_option('camera', 'cam')
    cmds.setParent('..')
    
    curr_panel = cmds.getPanel(withFocus=True)
    panel_type = cmds.getPanel(typeOf=curr_panel)
    # default to persp, otherwise try to find the cam of the current panel
    curr_cam = 'persp'
    if(panel_type == 'modelPanel'):
        curr_cam = cmds.modelEditor(curr_panel, q=True, camera=True)
    
    curr_cam = cmds.listRelatives(curr_cam, s=True)[0]
    select_current('cam', 'camera', curr_cam)
    
    # file format
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(160, 320))
    cmds.text(label='File Format', w=145, al='right')
    cmds.optionMenu('ff')
    cmds.menuItem(label='exr', parent='ff')
    cmds.menuItem(label='tif', parent='ff')
    cmds.menuItem(label='iff', parent='ff')
    cmds.menuItem(label='tga', parent='ff')
    cmds.menuItem(label='psd', parent='ff')
    cmds.setParent('..')
    
    # resolution
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(160, 160, 160))
    cmds.text(label='Resolution', w=145, al='right')
    cmds.intField('x_res', w=145, v=cmds.getAttr('defaultResolution.width'))
    cmds.intField('y_res', w=145, v=cmds.getAttr('defaultResolution.height'))
    cmds.setParent('..') # this "ends" or "closes" the current layout (rowLayout)
    
    # start and end frame, by, padding  
    cmds.separator(h=15)
    cmds.rowLayout(numberOfColumns=4, columnWidth4=(160, 160, 160, 160))
    cmds.text(label='Start Frame', w=145, al='center')
    cmds.text(label='End Frame', w=145, al='center')
    cmds.text(label='By Frame Step', w=145, al='center')
    cmds.text(label='Padding', w=145, al='center')
    cmds.setParent('..') # this "ends" or "closes" the current layout (rowLayout)
    cmds.rowLayout(numberOfColumns=4, columnWidth4=(160, 160, 160, 160))
    cmds.intField('start_frame', w=145, v=cmds.getAttr('defaultRenderGlobals.startFrame'))
    cmds.intField('end_frame', w=145, v=cmds.getAttr('defaultRenderGlobals.endFrame'))
    cmds.intField('by', w=145, v=cmds.getAttr('defaultRenderGlobals.byFrameStep'))
    # set default padding to 4
    cmds.setAttr('defaultRenderGlobals.extensionPadding', 4)
    cmds.intField('padding', w=145, v=cmds.getAttr('defaultRenderGlobals.extensionPadding'))
    cmds.setParent('..') # this "ends" or "closes" the current layout (rowLayout)
    
    # scroll field to display commands
    cmds.separator(h=15)
    cmds.scrollField('commands', editable=True, wordWrap=True, tx='', w=640)
    
    # create buttons
    cmds.separator(h=15)
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(213, 214, 213))
    cmds.button(label='Append Command', w=213, h=30, command=add_command)
    cmds.button(label='Clear All', w=214, h=30, command=clear)
    cmds.button(label='Save Script', w=213, h=30, command=save_script)
    cmds.setParent('..')
    cmds.separator(h=15)
    
    cmds.showWindow(window)
    
def sel_render_dir(*args):
    """opens a file browser to select the target directory for rendered files"""
    image_directory = cmds.workspace(q=True, rd=True)
    image_directory = os.path.join(image_directory, 'images', '')
    render_dir = cmds.fileDialog2(ds=2, dir=image_directory, fm=3)
    render_dir = os.path.join(render_dir[0], '')
    cmds.textField('render_dir_field', edit=True, tx=render_dir)

def add_command(*args):
    """gets values from text fields and generates a Render command"""
    rd = cmds.textField('render_dir_field', q=True, tx=True)
    name = cmds.textField('name', q=True, tx=True)
    rend = cmds.optionMenu('renderer', q=True, v=True)
    s = cmds.intField('start_frame', q=True, v=True)
    e = cmds.intField('end_frame', q=True, v=True)
    b = cmds.intField('by', q=True, v=True)
    p = cmds.intField('padding', q=True, v=True)
    x_res = cmds.intField('x_res', q=True, v=True)
    y_res = cmds.intField('y_res', q=True, v=True)
    ff = cmds.optionMenu('ff', q=True, v=True)
    rl = cmds.optionMenu('rl', q=True, v=True)
    cam = cmds.optionMenu('cam', q=True, v=True)
    file = cmds.file(q=True, sn=True)
    
    # big string format
    comm = 'Render -v 0 -rd {0} -im {1} -r {2} -s {3} -e {4} -b {5} -pad {6} -x {7} -y {8} -of {9} -cam {10} -rl {11} {12};\n'.format(rd, name, rend, s, e, b, p, x_res, y_res, ff, cam, rl, file)
    
    # get the current commands and add on the new one
    curr_commands = cmds.scrollField('commands', q=True, tx=True)
    curr_commands += comm
    
    cmds.scrollField('commands', edit=True, tx=curr_commands)

def clear(*args):
    """clears the command textarea"""
    cmds.scrollField('commands', edit=True, tx='')

def save_script(*args):
    """saves commands as a shell script in your data directory as render.sh"""
    data_directory = cmds.workspace(q=True, rd=True)
    data_file = os.path.join(data_directory, 'data', 'render.sh')
    f = open(data_file, 'w')
    f.write(cmds.scrollField('commands', q=True, tx=True))
    f.close()
    
def update_name(*args):
    """updates the name based on currently selected render layer"""
    rl = cmds.optionMenu('rl', q=True, v=True)
    name = cmds.textField('name', e=True, tx=rl)

def populate_option(t, p):
    """populates optionMenu items given a type of object (t) and a parent menu (p)"""
    options = cmds.ls(type=t)
    for o in options:
        cmds.menuItem(label=o, parent=p)

def select_current(option_menu_name, t, current):
    """selects the appropriate item in a optionMenu"""
    options = cmds.ls(type=t)
    for x in range(len(options)):
        if(options[x] == current):
            cmds.optionMenu(option_menu_name, edit=True, sl=x+1)

def main():
    """calls the UI function to generate the UI"""
UI()
