""" visualize - graphical representation of broaster generated data

Uses pyqt and guiqwt for fast, configurable graphs.
"""

import sys
import numpy

from guiqwt import plot
from guiqwt import styles
from guiqwt import curve
from guiqwt import builder

from PyQt4 import QtGui, QtCore, QtSvg

from boardtester import broaster

class SimpleHeatMap(QtGui.QWidget):
    """ Wrappers for creating guiqwt heatmaps from numpy data.
    """
    def __init__(self):
        super(SimpleHeatMap, self).__init__()
        self.setupUI()
        self.show()

    def setupUI(self):
        """ Place an guiqwt imagedialog on the widget.
        """
        self.mainImageDialog = plot.ImageDialog(toolbar=True, edit=True,
            wintitle="Image Dialog")

        self.plot = self.mainImageDialog.get_plot()
    
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mainImageDialog)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 800, 800)
       
    def render_image(self, data_list):
        """ With a two dimensional data set, create and imageitem and
        add it to the image widget.
        """ 
        bmi = builder.make.image
        self.image = bmi(data_list)
        self.plot.add_item(self.image)
        self.plot.do_autoscale()

    def total_pixels(self):
        """ Show the heatmap of all pixel values
        """
        proc = broaster.ProcessBroaster()
        self.node_root = "exam_results/kali"
        result = proc.collate_pixels(self.node_root)
        data = numpy.array(result["all_data"]).astype(float)
        
        self.render_image(data)
        
        
class SimpleLineGraph(QtGui.QWidget):
    """ Various wrappers and helper functions for generating single line
    curves, multiple curves with gap data, and point coverage graphs
    from the same data source.
    """
    def __init__(self):
        super(SimpleLineGraph, self).__init__()

        self.setupUI()
        self.show()

    def setupUI(self):
        self.mainCurveDialog = plot.CurveDialog(toolbar=True,
            edit=True, wintitle="Main Dialog")

        self.plot = self.mainCurveDialog.get_plot()
        
        self.chart_param = styles.CurveParam()
        self.chart_param.label = "Data"
        self.chart_param.line.color = "Blue"
        
        #self.plot.set_axis_limits(0, 0, 65535)
        #self.plot.set_axis_limits(2, 0, len(self.x))
        #self.plot.set_axis_title(0, "Intensity (auto)")
        #self.plot.set_axis_title(2, "Pixel")

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mainCurveDialog)
        self.setLayout(vbox)

        self.setGeometry(100, 100, 800, 300)
        
    def render_graph(self, data_list):
        """ With a one dimensional list, update the existing curve,
        refresh the graph.
        """
        x_axis = range(len(data_list))
        self.curve = curve.CurveItem(self.chart_param)
        self.curve.set_data(x_axis, data_list)
        self.plot.add_item(self.curve)
        self.plot.do_autoscale()

    def render_point_graph(self, data_list):
        """ With one dimesional data list, create a new curve that is
        displayed with points, this is designed to then let the user
        specify a top and bottom scale to show the data and the gaps in
        the data.
        """

        data_x = range(len(data_list))
        data_y = data_list
        bmc = builder.make.curve
        self.point_curve = bmc(data_x, data_y, linestyle="NoPen",
            linewidth=0.1, marker="Diamond", markersize=5.0)

        #self.point_curve.set_data(data_x, data_y)
        
        self.plot.add_item(self.point_curve)
        self.plot.do_autoscale()

    def render_gaps(self, data_list):
        """ One dimenstional data, where the list has numpy.nan where no
        data was collected. Create a series of non-continguous graphs
        from the mixed intensity/nan data.
        """
        bmc = builder.make.curve

        orig_position = 0
                
        y_axis = []
        x_axis = []

        while orig_position < len(data_list):
            curr_value = data_list[orig_position]

            #print "value is data at %s" % curr_value
            if curr_value != -9999:
                #print "Adding data at %s" % orig_position
                y_axis.append(curr_value)
                x_axis.append(orig_position)
    
            else:
                #print "Found end nan at %s" % curr_value
                new_curve = bmc(x_axis, y_axis, color="red")
                self.plot.add_item(new_curve)
                y_axis = []
                x_axis = []
        
            orig_position += 1
       
        # Add the final curve if it contains data
        if len(x_axis) != 0:
            new_curve = bmc(x_axis, y_axis, color="red")
            self.plot.add_item(new_curve)
 
        self.plot.do_autoscale()

    def total_averages(self):
        # Add in a group of known test results
        proc = broaster.ProcessBroaster()

        #self.node_root = "exam_results/test_example_node"
        self.node_root = "exam_results/kali"

        # Average value of entire line over every exam, showing gaps for
        # missing data/bad power ons
        result = proc.process_in_order(self.node_root)
        self.render_gaps(result["total_line_averages"])

        # Average value of each pixel over every exam
        #result = proc.process_in_order_get_pixels(self.node_root)
        #self.render_gaps(result["average_pixels"])
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    grp = SimpleLineGraph()
    grp.total_averages()

    #shm = SimpleHeatMap()
    #shm.total_pixels()

    sys.exit(app.exec_())
