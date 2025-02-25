# Analyse Data

In here we provide some heat flow specific analysis functionalities like Digital Borehole and 2D Profile.

**Note:** Both functionalities will display a popup containing a graph. The popup itself cannot be moved, but it is attached to a marker that can be relocated by dragging it.

## Digital Borehole

Users are allowed to draw a point on the map and calcaulate the temperature as function of depth. The calculation is based on the Bootstrapping Method which is described more in detail here 
<!-- TODO: Add source to bootstrap method Chapman, P. L. and Hinkley, D. V. (1986) The double bootstrap, pivots and confidence limits. Report 26. Center for Statistical Sciences, University of Texas at Austin. -->

<math display="block">
        <mi>T</mi>
        <mo>=</mo>
        <mrow>
          <mmultiscripts>
            <mn>T</mn>
            <mn>0</mn>
          </mmultiscripts>
          <mo>+</mo>
          <munderover>
            <mo>∑</mo>
            <mrow>
              <mi>i</mi>
              <mo>=</mo>
              <mn>1</mn>
            </mrow>
            <mrow>
              <mo>n</mo>
            </mrow>
          </munderover>
          <mo>(</mo>
          <mfrac>
            <mrow>
              <msup>
                <mrow>
                  <msub>
                    <mn>q</mn>
                    <mn
                      ><mmultiscripts>
                        <mn>i-1</mn>
                      </mmultiscripts>
                    </mn>
                  </msub>
                </mrow>
              </msup>
              <msup>
                <mrow>
                  <msub>
                    <mn>&Delta;</mn>
                    <mn
                      ><mmultiscripts>
                        <mn>Z</mn>
                        <mn>i</mn>
                      </mmultiscripts>
                    </mn>
                  </msub>
                </mrow>
              </msup>
            </mrow>
            <msup>
              <munder>
                <msup>
                  <mrow>
                    <msub>
                      <mn>k</mn>
                      <mn
                        ><mmultiscripts>
                          <mn>i</mn>
                        </mmultiscripts>
                      </mn>
                    </msub>
                  </mrow>
                </msup>
              </munder>
            </msup>
          </mfrac>
          <mo>-</mo>
          <mfrac>
            <mrow>
              <msup>
                <mrow>
                  <msub>
                    <mn>A</mn>
                    <mn
                      ><mmultiscripts>
                        <mn>i</mn>
                      </mmultiscripts>
                    </mn>
                  </msub>
                </mrow>
              </msup>
              <msup>
                <mrow>
                  <msub>
                    <mn>&Delta;</mn>
                    <mn
                      ><mmultiscripts>
                        <mn>Z</mn>
                        <mn>i</mn>
                      </mmultiscripts>
                    </mn>
                  </msub>
                </mrow>
                <mn>2</mn>
              </msup>
            </mrow>
            <msup>
              <msup>
                <mrow>
                  <msub>
                    <mn>2k</mn>
                    <mn
                      ><mmultiscripts>
                        <mn>i</mn>
                      </mmultiscripts>
                    </mn>
                  </msub>
                </mrow>
              </msup>
            </msup>
          </mfrac>
          <mo>)</mo>
        </mrow>
      </math>

### Draw Toolbox

Specify the location by placing a point on the map. Only one point can be placed at a time, any previously drawn points will be deleted.

<img src="../../docs/_static/_mapping/digital-borehole_toolbox.PNG" alt="Circle color" width="50%"/>

### Customize Graph

Once a point is placed, a graph is generated. As per the equation above, each parameter for the layer can be customized within this tab.

<img src="../../docs/_static/_mapping/digital-borehole_custom_parameter.PNG" alt="Circle color" width="50%"/>

### About Bootstrapping

Here, you will find information about the method.

<img src="../../docs/_static/_mapping/digital-borehole_about.PNG" alt="Circle color" width="50%"/>

### Results

As a result, a popup will appear on the map at the drawn point. The graph will update automatically if you modify any parameters for the layer within the table.

<img src="../../docs/_static/_mapping/digital-borehole_result.PNG" alt="Circle color" width="100%"/>

## 2D Profile

The 2D Proifle projects values of existing points within a threshold distance to a useres drawn line on the line and displays.

### Setup

<img src="../../docs/_static/_mapping/2d-profile-setup.PNG" alt="Circle color" width="50%"/>

### Draw Toolbox

Draw a line to project existing points within a threshold onto the line, generating the 2D profile. Only one line can be active at a time, previously drawn lines will be deleted. Additionally, a line can consist of only two points. If more than two points are drawn, the first and last point will be used.

<img src="../../docs/_static/_mapping/2d-profile-toolbox.PNG" alt="Circle color" width="50%"/>

### About 2D Profile

Here, you can find information about the algorithm used to calculate the graph.

<img src="../../docs/_static/_mapping/2d-profile-about.PNG" alt="Circle color" width="50%"/>

### Results

The results will be a popup showing the points within a users defined threshold. The logic behind the graph is shown in the following figure.

<img src="../../docs/_static/_mapping/about_2D_profile_.svg" alt="triangle with all three sides equal" width="50%"/>


<br><br>
The resulting 2D Profile in the app looks like this.

<img src="../../docs/_static/_mapping/2d-profile-results.PNG" alt="Circle color" width="100%"/>
