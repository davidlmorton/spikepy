

from spikepy import session

s = session.Session()
s.open_file('/home/davidmorton/Desktop/Sample Data/278-Turtle_NI_Cortex_II-data.tet')
s.visualize('2', 'P', invert_colors=True)
s.run(stage_name='detection_filter')
s.visualize('2', 'P', logscale=False)
