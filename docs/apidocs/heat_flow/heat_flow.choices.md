# {py:mod}`heat_flow.choices`

```{py:module} heat_flow.choices
```

```{autodoc2-docstring} heat_flow.choices
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeatFlowMethod <heat_flow.choices.HeatFlowMethod>`
  - ```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod
    :summary:
    ```
* - {py:obj}`ProbeType <heat_flow.choices.ProbeType>`
  - ```{autodoc2-docstring} heat_flow.choices.ProbeType
    :summary:
    ```
* - {py:obj}`HeatFlowTransferMechanism <heat_flow.choices.HeatFlowTransferMechanism>`
  - ```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism
    :summary:
    ```
* - {py:obj}`GeographicEnvironment <heat_flow.choices.GeographicEnvironment>`
  - ```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment
    :summary:
    ```
* - {py:obj}`ExplorationMethod <heat_flow.choices.ExplorationMethod>`
  - ```{autodoc2-docstring} heat_flow.choices.ExplorationMethod
    :summary:
    ```
* - {py:obj}`ExplorationPurpose <heat_flow.choices.ExplorationPurpose>`
  - ```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose
    :summary:
    ```
* - {py:obj}`TemperatureMethod <heat_flow.choices.TemperatureMethod>`
  - ```{autodoc2-docstring} heat_flow.choices.TemperatureMethod
    :summary:
    ```
* - {py:obj}`TemperatureCorrection <heat_flow.choices.TemperatureCorrection>`
  - ```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection
    :summary:
    ```
* - {py:obj}`ConductivitySource <heat_flow.choices.ConductivitySource>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivitySource
    :summary:
    ```
* - {py:obj}`ConductivityMethod <heat_flow.choices.ConductivityMethod>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivityMethod
    :summary:
    ```
* - {py:obj}`ConductivityLocation <heat_flow.choices.ConductivityLocation>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivityLocation
    :summary:
    ```
* - {py:obj}`ConductivitySaturation <heat_flow.choices.ConductivitySaturation>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation
    :summary:
    ```
* - {py:obj}`ConductivityPTConditions <heat_flow.choices.ConductivityPTConditions>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions
    :summary:
    ```
* - {py:obj}`ConductivityStrategy <heat_flow.choices.ConductivityStrategy>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy
    :summary:
    ```
* - {py:obj}`GenericFlagChoices <heat_flow.choices.GenericFlagChoices>`
  - ```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices
    :summary:
    ```
* - {py:obj}`InSituFlagChoices <heat_flow.choices.InSituFlagChoices>`
  - ```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices
    :summary:
    ```
* - {py:obj}`TemperatureFlagChoices <heat_flow.choices.TemperatureFlagChoices>`
  - ```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ConductivityMethodFormChoices <heat_flow.choices.ConductivityMethodFormChoices>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivityMethodFormChoices
    :summary:
    ```
* - {py:obj}`ConductivityPTFunction <heat_flow.choices.ConductivityPTFunction>`
  - ```{autodoc2-docstring} heat_flow.choices.ConductivityPTFunction
    :summary:
    ```
````

### API

`````{py:class} HeatFlowMethod()
:canonical: heat_flow.choices.HeatFlowMethod

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod.__init__
```

````{py:attribute} FOURIER
:canonical: heat_flow.choices.HeatFlowMethod.FOURIER
:value: >
   ('FOU',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod.FOURIER
```

````

````{py:attribute} PRODUCT
:canonical: heat_flow.choices.HeatFlowMethod.PRODUCT
:value: >
   ('PRO',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod.PRODUCT
```

````

````{py:attribute} BULLARD
:canonical: heat_flow.choices.HeatFlowMethod.BULLARD
:value: >
   ('BUL',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod.BULLARD
```

````

````{py:attribute} BOOTSTRAP
:canonical: heat_flow.choices.HeatFlowMethod.BOOTSTRAP
:value: >
   ('BOO',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod.BOOTSTRAP
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.HeatFlowMethod.OTHER
:value: >
   ('OTH',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowMethod.OTHER
```

````

`````

`````{py:class} ProbeType()
:canonical: heat_flow.choices.ProbeType

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ProbeType
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ProbeType.__init__
```

````{py:attribute} CORER
:canonical: heat_flow.choices.ProbeType.CORER
:value: >
   ('COR',)

```{autodoc2-docstring} heat_flow.choices.ProbeType.CORER
```

````

````{py:attribute} BULLARD
:canonical: heat_flow.choices.ProbeType.BULLARD
:value: >
   ('BUL',)

```{autodoc2-docstring} heat_flow.choices.ProbeType.BULLARD
```

````

````{py:attribute} VIOLIN_BOW
:canonical: heat_flow.choices.ProbeType.VIOLIN_BOW
:value: >
   ('VIO',)

```{autodoc2-docstring} heat_flow.choices.ProbeType.VIOLIN_BOW
```

````

````{py:attribute} EWING
:canonical: heat_flow.choices.ProbeType.EWING
:value: >
   ('EWI',)

```{autodoc2-docstring} heat_flow.choices.ProbeType.EWING
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ProbeType.OTHER
:value: >
   ('OTH',)

```{autodoc2-docstring} heat_flow.choices.ProbeType.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ProbeType.UNSPECIFIED
:value: >
   ('UNS',)

```{autodoc2-docstring} heat_flow.choices.ProbeType.UNSPECIFIED
```

````

`````

`````{py:class} HeatFlowTransferMechanism()
:canonical: heat_flow.choices.HeatFlowTransferMechanism

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism.__init__
```

````{py:attribute} CONDUCTIVE
:canonical: heat_flow.choices.HeatFlowTransferMechanism.CONDUCTIVE
:value: >
   ('Conductive',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism.CONDUCTIVE
```

````

````{py:attribute} CONVECTIVE
:canonical: heat_flow.choices.HeatFlowTransferMechanism.CONVECTIVE
:value: >
   ('Convective unspecified',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism.CONVECTIVE
```

````

````{py:attribute} CONVECTIVE_UPFLOW
:canonical: heat_flow.choices.HeatFlowTransferMechanism.CONVECTIVE_UPFLOW
:value: >
   ('Convective upflow',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism.CONVECTIVE_UPFLOW
```

````

````{py:attribute} CONVECTIVE_DOWNFLOW
:canonical: heat_flow.choices.HeatFlowTransferMechanism.CONVECTIVE_DOWNFLOW
:value: >
   ('Convective downflow',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism.CONVECTIVE_DOWNFLOW
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.HeatFlowTransferMechanism.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.HeatFlowTransferMechanism.UNSPECIFIED
```

````

`````

`````{py:class} GeographicEnvironment()
:canonical: heat_flow.choices.GeographicEnvironment

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment.__init__
```

````{py:attribute} ONSHORE_CONTINENTAL
:canonical: heat_flow.choices.GeographicEnvironment.ONSHORE_CONTINENTAL
:value: >
   ('Onshore (continental)',)

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment.ONSHORE_CONTINENTAL
```

````

````{py:attribute} ONSHORE_LAKE
:canonical: heat_flow.choices.GeographicEnvironment.ONSHORE_LAKE
:value: >
   ('Onshore (lake, river, etc.)',)

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment.ONSHORE_LAKE
```

````

````{py:attribute} OFFSHORE_CONTINENTAL
:canonical: heat_flow.choices.GeographicEnvironment.OFFSHORE_CONTINENTAL
:value: >
   ('Offshore (continental)',)

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment.OFFSHORE_CONTINENTAL
```

````

````{py:attribute} OFFSHORE_MARINE
:canonical: heat_flow.choices.GeographicEnvironment.OFFSHORE_MARINE
:value: >
   ('Offshore (marine)',)

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment.OFFSHORE_MARINE
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.GeographicEnvironment.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.GeographicEnvironment.UNSPECIFIED
```

````

`````

`````{py:class} ExplorationMethod()
:canonical: heat_flow.choices.ExplorationMethod

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.__init__
```

````{py:attribute} DRILLING
:canonical: heat_flow.choices.ExplorationMethod.DRILLING
:value: >
   ('Drilling',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.DRILLING
```

````

````{py:attribute} MINING
:canonical: heat_flow.choices.ExplorationMethod.MINING
:value: >
   ('Mining',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.MINING
```

````

````{py:attribute} TUNNELING
:canonical: heat_flow.choices.ExplorationMethod.TUNNELING
:value: >
   ('Tunneling',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.TUNNELING
```

````

````{py:attribute} PROBING_ONSHORE
:canonical: heat_flow.choices.ExplorationMethod.PROBING_ONSHORE
:value: >
   ('Probing (onshore/lake, river, etc.)',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.PROBING_ONSHORE
```

````

````{py:attribute} PROBING_OFFSHORE
:canonical: heat_flow.choices.ExplorationMethod.PROBING_OFFSHORE
:value: >
   ('Probing (offshore/ocean)',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.PROBING_OFFSHORE
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ExplorationMethod.OTHER
:value: >
   ('Other (specify in comments)',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ExplorationMethod.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.ExplorationMethod.UNSPECIFIED
```

````

`````

`````{py:class} ExplorationPurpose()
:canonical: heat_flow.choices.ExplorationPurpose

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.__init__
```

````{py:attribute} HYDROCARBON
:canonical: heat_flow.choices.ExplorationPurpose.HYDROCARBON
:value: >
   ('Hydrocarbon',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.HYDROCARBON
```

````

````{py:attribute} UNDERGROUND_STORAGE
:canonical: heat_flow.choices.ExplorationPurpose.UNDERGROUND_STORAGE
:value: >
   ('Underground storage',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.UNDERGROUND_STORAGE
```

````

````{py:attribute} GEOTHERMAL
:canonical: heat_flow.choices.ExplorationPurpose.GEOTHERMAL
:value: >
   ('Geothermal',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.GEOTHERMAL
```

````

````{py:attribute} GROUNDWATER
:canonical: heat_flow.choices.ExplorationPurpose.GROUNDWATER
:value: >
   ('Groundwater',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.GROUNDWATER
```

````

````{py:attribute} MAPPING
:canonical: heat_flow.choices.ExplorationPurpose.MAPPING
:value: >
   ('Mapping',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.MAPPING
```

````

````{py:attribute} MINING
:canonical: heat_flow.choices.ExplorationPurpose.MINING
:value: >
   ('Mining',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.MINING
```

````

````{py:attribute} RESEARCH
:canonical: heat_flow.choices.ExplorationPurpose.RESEARCH
:value: >
   ('Research',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.RESEARCH
```

````

````{py:attribute} TUNNELING
:canonical: heat_flow.choices.ExplorationPurpose.TUNNELING
:value: >
   ('Tunneling',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.TUNNELING
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ExplorationPurpose.OTHER
:value: >
   ('Other (specify in comments)',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ExplorationPurpose.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.ExplorationPurpose.UNSPECIFIED
```

````

`````

`````{py:class} TemperatureMethod()
:canonical: heat_flow.choices.TemperatureMethod

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.__init__
```

````{py:attribute} LOGeq
:canonical: heat_flow.choices.TemperatureMethod.LOGeq
:value: >
   ('LOGeq',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.LOGeq
```

````

````{py:attribute} LOGpert
:canonical: heat_flow.choices.TemperatureMethod.LOGpert
:value: >
   ('LOGpert',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.LOGpert
```

````

````{py:attribute} cLOG
:canonical: heat_flow.choices.TemperatureMethod.cLOG
:value: >
   ('cLOG',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.cLOG
```

````

````{py:attribute} DTSeq
:canonical: heat_flow.choices.TemperatureMethod.DTSeq
:value: >
   ('DTSeq',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.DTSeq
```

````

````{py:attribute} DTSpert
:canonical: heat_flow.choices.TemperatureMethod.DTSpert
:value: >
   ('DTSpert',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.DTSpert
```

````

````{py:attribute} cDTS
:canonical: heat_flow.choices.TemperatureMethod.cDTS
:value: >
   ('cDTS',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.cDTS
```

````

````{py:attribute} BHT
:canonical: heat_flow.choices.TemperatureMethod.BHT
:value: >
   ('BHT',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.BHT
```

````

````{py:attribute} cBHT
:canonical: heat_flow.choices.TemperatureMethod.cBHT
:value: >
   ('cBHT',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.cBHT
```

````

````{py:attribute} DST
:canonical: heat_flow.choices.TemperatureMethod.DST
:value: >
   ('DST',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.DST
```

````

````{py:attribute} cDST
:canonical: heat_flow.choices.TemperatureMethod.cDST
:value: >
   ('cDST',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.cDST
```

````

````{py:attribute} RTDeq
:canonical: heat_flow.choices.TemperatureMethod.RTDeq
:value: >
   ('RTDeq',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.RTDeq
```

````

````{py:attribute} RTDpert
:canonical: heat_flow.choices.TemperatureMethod.RTDpert
:value: >
   ('RTDpert',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.RTDpert
```

````

````{py:attribute} cRTD
:canonical: heat_flow.choices.TemperatureMethod.cRTD
:value: >
   ('cRTD',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.cRTD
```

````

````{py:attribute} ODTT_PC
:canonical: heat_flow.choices.TemperatureMethod.ODTT_PC
:value: >
   ('ODTT-PC',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.ODTT_PC
```

````

````{py:attribute} ODTT_TP
:canonical: heat_flow.choices.TemperatureMethod.ODTT_TP
:value: >
   ('ODTT-TP',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.ODTT_TP
```

````

````{py:attribute} CPD
:canonical: heat_flow.choices.TemperatureMethod.CPD
:value: >
   ('CPD',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.CPD
```

````

````{py:attribute} XEN
:canonical: heat_flow.choices.TemperatureMethod.XEN
:value: >
   ('XEN',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.XEN
```

````

````{py:attribute} GTM
:canonical: heat_flow.choices.TemperatureMethod.GTM
:value: >
   ('GTM',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.GTM
```

````

````{py:attribute} BSR
:canonical: heat_flow.choices.TemperatureMethod.BSR
:value: >
   ('BSR',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.BSR
```

````

````{py:attribute} SUR
:canonical: heat_flow.choices.TemperatureMethod.SUR
:value: >
   ('SUR',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.SUR
```

````

````{py:attribute} OTH
:canonical: heat_flow.choices.TemperatureMethod.OTH
:value: >
   ('OTH',)

```{autodoc2-docstring} heat_flow.choices.TemperatureMethod.OTH
```

````

`````

`````{py:class} TemperatureCorrection()
:canonical: heat_flow.choices.TemperatureCorrection

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.__init__
```

````{py:attribute} HORNER
:canonical: heat_flow.choices.TemperatureCorrection.HORNER
:value: >
   ('Horner plot',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.HORNER
```

````

````{py:attribute} CYLINDER
:canonical: heat_flow.choices.TemperatureCorrection.CYLINDER
:value: >
   ('Cylinder source method',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.CYLINDER
```

````

````{py:attribute} LINE
:canonical: heat_flow.choices.TemperatureCorrection.LINE
:value: >
   ('Line source explosion method',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.LINE
```

````

````{py:attribute} INVERSE
:canonical: heat_flow.choices.TemperatureCorrection.INVERSE
:value: >
   ('Inverse numerical modelling',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.INVERSE
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.TemperatureCorrection.OTHER
:value: >
   ('Other published correction',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.TemperatureCorrection.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.UNSPECIFIED
```

````

````{py:attribute} NOT_CORRECTED
:canonical: heat_flow.choices.TemperatureCorrection.NOT_CORRECTED
:value: >
   ('not corrected',)

```{autodoc2-docstring} heat_flow.choices.TemperatureCorrection.NOT_CORRECTED
```

````

`````

`````{py:class} ConductivitySource()
:canonical: heat_flow.choices.ConductivitySource

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ConductivitySource
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.__init__
```

````{py:attribute} INSITU_PROBE
:canonical: heat_flow.choices.ConductivitySource.INSITU_PROBE
:value: >
   ('In-situ probe',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.INSITU_PROBE
```

````

````{py:attribute} CORE_LOG
:canonical: heat_flow.choices.ConductivitySource.CORE_LOG
:value: >
   ('Core-log integration',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.CORE_LOG
```

````

````{py:attribute} CORE_SAMPLES
:canonical: heat_flow.choices.ConductivitySource.CORE_SAMPLES
:value: >
   ('Core samples',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.CORE_SAMPLES
```

````

````{py:attribute} CUTTING_SAMPLES
:canonical: heat_flow.choices.ConductivitySource.CUTTING_SAMPLES
:value: >
   ('Cutting samples',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.CUTTING_SAMPLES
```

````

````{py:attribute} OUTCROP_SAMPLES
:canonical: heat_flow.choices.ConductivitySource.OUTCROP_SAMPLES
:value: >
   ('Outcrop samples',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.OUTCROP_SAMPLES
```

````

````{py:attribute} WELL_LOG
:canonical: heat_flow.choices.ConductivitySource.WELL_LOG
:value: >
   ('Well-log interpretation',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.WELL_LOG
```

````

````{py:attribute} MINERAL_COMPUTATION
:canonical: heat_flow.choices.ConductivitySource.MINERAL_COMPUTATION
:value: >
   ('Mineral computation',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.MINERAL_COMPUTATION
```

````

````{py:attribute} ASSUMED_FROM_LITERATURE
:canonical: heat_flow.choices.ConductivitySource.ASSUMED_FROM_LITERATURE
:value: >
   ('Assumed from literature',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.ASSUMED_FROM_LITERATURE
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ConductivitySource.OTHER
:value: >
   ('Other (specify)',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ConductivitySource.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySource.UNSPECIFIED
```

````

`````

`````{py:class} ConductivityMethod()
:canonical: heat_flow.choices.ConductivityMethod

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.__init__
```

````{py:attribute} LAB_POINT
:canonical: heat_flow.choices.ConductivityMethod.LAB_POINT
:value: >
   ('Lab - point source',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.LAB_POINT
```

````

````{py:attribute} LAB_LINE_FULL
:canonical: heat_flow.choices.ConductivityMethod.LAB_LINE_FULL
:value: >
   ('Lab - line source / full space',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.LAB_LINE_FULL
```

````

````{py:attribute} LAB_LINE_HALF
:canonical: heat_flow.choices.ConductivityMethod.LAB_LINE_HALF
:value: >
   ('Lab - line source / half space',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.LAB_LINE_HALF
```

````

````{py:attribute} LAB_PLANE_FULL
:canonical: heat_flow.choices.ConductivityMethod.LAB_PLANE_FULL
:value: >
   ('Lab - plane source / full space',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.LAB_PLANE_FULL
```

````

````{py:attribute} LAB_PLANE_HALF
:canonical: heat_flow.choices.ConductivityMethod.LAB_PLANE_HALF
:value: >
   ('Lab - plane source / half space',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.LAB_PLANE_HALF
```

````

````{py:attribute} LAB_OTHER
:canonical: heat_flow.choices.ConductivityMethod.LAB_OTHER
:value: >
   ('Lab - other',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.LAB_OTHER
```

````

````{py:attribute} PROBE_PULSE
:canonical: heat_flow.choices.ConductivityMethod.PROBE_PULSE
:value: >
   ('Probe - pulse technique',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.PROBE_PULSE
```

````

````{py:attribute} WELL_LOG_DETERMINISTIC
:canonical: heat_flow.choices.ConductivityMethod.WELL_LOG_DETERMINISTIC
:value: >
   ('Well-log - deterministic approach',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.WELL_LOG_DETERMINISTIC
```

````

````{py:attribute} WELL_LOG_EMPIRICAL
:canonical: heat_flow.choices.ConductivityMethod.WELL_LOG_EMPIRICAL
:value: >
   ('Well-log - empirical equation',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.WELL_LOG_EMPIRICAL
```

````

````{py:attribute} ESTIMATION_CHLORINE
:canonical: heat_flow.choices.ConductivityMethod.ESTIMATION_CHLORINE
:value: >
   ('Estimation - from chlorine content',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.ESTIMATION_CHLORINE
```

````

````{py:attribute} ESTIMATION_WATER
:canonical: heat_flow.choices.ConductivityMethod.ESTIMATION_WATER
:value: >
   ('Estimation - from water content/porosity',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.ESTIMATION_WATER
```

````

````{py:attribute} ESTIMATION_LITHOLOGY
:canonical: heat_flow.choices.ConductivityMethod.ESTIMATION_LITHOLOGY
:value: >
   ('Estimation - from lithology and literature',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.ESTIMATION_LITHOLOGY
```

````

````{py:attribute} ESTIMATION_MINERAL
:canonical: heat_flow.choices.ConductivityMethod.ESTIMATION_MINERAL
:value: >
   ('Estimation - from mineral composition',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.ESTIMATION_MINERAL
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ConductivityMethod.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.ConductivityMethod.UNSPECIFIED
```

````

`````

````{py:data} ConductivityMethodFormChoices
:canonical: heat_flow.choices.ConductivityMethodFormChoices
:value: >
   [(), (), (), (), ()]

```{autodoc2-docstring} heat_flow.choices.ConductivityMethodFormChoices
```

````

`````{py:class} ConductivityLocation()
:canonical: heat_flow.choices.ConductivityLocation

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ConductivityLocation
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ConductivityLocation.__init__
```

````{py:attribute} ACTUAL
:canonical: heat_flow.choices.ConductivityLocation.ACTUAL
:value: >
   ('Actual heat-flow location',)

```{autodoc2-docstring} heat_flow.choices.ConductivityLocation.ACTUAL
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ConductivityLocation.OTHER
:value: >
   ('Other location',)

```{autodoc2-docstring} heat_flow.choices.ConductivityLocation.OTHER
```

````

````{py:attribute} LITERATURE
:canonical: heat_flow.choices.ConductivityLocation.LITERATURE
:value: >
   ('Literature/unspecified',)

```{autodoc2-docstring} heat_flow.choices.ConductivityLocation.LITERATURE
```

````

`````

`````{py:class} ConductivitySaturation()
:canonical: heat_flow.choices.ConductivitySaturation

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.__init__
```

````{py:attribute} SATURATED_IN_SITU
:canonical: heat_flow.choices.ConductivitySaturation.SATURATED_IN_SITU
:value: >
   ('Saturated measured in-situ',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.SATURATED_IN_SITU
```

````

````{py:attribute} RECOVERED
:canonical: heat_flow.choices.ConductivitySaturation.RECOVERED
:value: >
   ('Recovered',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.RECOVERED
```

````

````{py:attribute} SATURATED_MEASURED
:canonical: heat_flow.choices.ConductivitySaturation.SATURATED_MEASURED
:value: >
   ('Saturated measured',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.SATURATED_MEASURED
```

````

````{py:attribute} SATURATED_CALCULATED
:canonical: heat_flow.choices.ConductivitySaturation.SATURATED_CALCULATED
:value: >
   ('Saturated calculated',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.SATURATED_CALCULATED
```

````

````{py:attribute} DRY_MEASURED
:canonical: heat_flow.choices.ConductivitySaturation.DRY_MEASURED
:value: >
   ('Dry measured',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.DRY_MEASURED
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ConductivitySaturation.OTHER
:value: >
   ('Other (specify)',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ConductivitySaturation.UNSPECIFIED
:value: >
   ('Unspecified',)

```{autodoc2-docstring} heat_flow.choices.ConductivitySaturation.UNSPECIFIED
```

````

`````

`````{py:class} ConductivityPTConditions()
:canonical: heat_flow.choices.ConductivityPTConditions

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.__init__
```

````{py:attribute} UNRECORDED
:canonical: heat_flow.choices.ConductivityPTConditions.UNRECORDED
:value: >
   ('Unrecorded ambient pT conditions',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.UNRECORDED
```

````

````{py:attribute} RECORDED
:canonical: heat_flow.choices.ConductivityPTConditions.RECORDED
:value: >
   ('Recorded ambient pT conditions',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.RECORDED
```

````

````{py:attribute} ACTUAL
:canonical: heat_flow.choices.ConductivityPTConditions.ACTUAL
:value: >
   ('Actual in-situ (pT) conditions',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.ACTUAL
```

````

````{py:attribute} REPLICATED_P
:canonical: heat_flow.choices.ConductivityPTConditions.REPLICATED_P
:value: >
   ('Replicated in-situ (p)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.REPLICATED_P
```

````

````{py:attribute} REPLICATED_T
:canonical: heat_flow.choices.ConductivityPTConditions.REPLICATED_T
:value: >
   ('Replicated in-situ (T)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.REPLICATED_T
```

````

````{py:attribute} REPLICATED_PT
:canonical: heat_flow.choices.ConductivityPTConditions.REPLICATED_PT
:value: >
   ('Replicated in-situ (pT)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.REPLICATED_PT
```

````

````{py:attribute} CORRECTED_P
:canonical: heat_flow.choices.ConductivityPTConditions.CORRECTED_P
:value: >
   ('Corrected in-situ (p)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.CORRECTED_P
```

````

````{py:attribute} CORRECTED_T
:canonical: heat_flow.choices.ConductivityPTConditions.CORRECTED_T
:value: >
   ('Corrected in-situ (T)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.CORRECTED_T
```

````

````{py:attribute} CORRECTED_PT
:canonical: heat_flow.choices.ConductivityPTConditions.CORRECTED_PT
:value: >
   ('Corrected in-situ (pT)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.CORRECTED_PT
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ConductivityPTConditions.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.ConductivityPTConditions.UNSPECIFIED
```

````

`````

`````{py:class} ConductivityStrategy()
:canonical: heat_flow.choices.ConductivityStrategy

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.__init__
```

````{py:attribute} RANDOM
:canonical: heat_flow.choices.ConductivityStrategy.RANDOM
:value: >
   ('Random or periodic depth sampling (number)',)

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.RANDOM
```

````

````{py:attribute} CHARACTERIZE
:canonical: heat_flow.choices.ConductivityStrategy.CHARACTERIZE
:value: >
   ('Characterize formation conductivities',)

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.CHARACTERIZE
```

````

````{py:attribute} WELL_LOG
:canonical: heat_flow.choices.ConductivityStrategy.WELL_LOG
:value: >
   ('Well log interpretation',)

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.WELL_LOG
```

````

````{py:attribute} COMPUTATION
:canonical: heat_flow.choices.ConductivityStrategy.COMPUTATION
:value: >
   ('Computation from probe sensing',)

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.COMPUTATION
```

````

````{py:attribute} OTHER
:canonical: heat_flow.choices.ConductivityStrategy.OTHER
:value: >
   ('Other',)

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.OTHER
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.ConductivityStrategy.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.ConductivityStrategy.UNSPECIFIED
```

````

`````

````{py:data} ConductivityPTFunction
:canonical: heat_flow.choices.ConductivityPTFunction
:value: >
   [(), (), (), ()]

```{autodoc2-docstring} heat_flow.choices.ConductivityPTFunction
```

````

`````{py:class} GenericFlagChoices()
:canonical: heat_flow.choices.GenericFlagChoices

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices.__init__
```

````{py:attribute} PRESENT_CORRECTED
:canonical: heat_flow.choices.GenericFlagChoices.PRESENT_CORRECTED
:value: >
   ('Present and corrected',)

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices.PRESENT_CORRECTED
```

````

````{py:attribute} PRESENT_NOT_CORRECTED
:canonical: heat_flow.choices.GenericFlagChoices.PRESENT_NOT_CORRECTED
:value: >
   ('Present and not corrected',)

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices.PRESENT_NOT_CORRECTED
```

````

````{py:attribute} PRESENT_NOT_SIGNIFICANT
:canonical: heat_flow.choices.GenericFlagChoices.PRESENT_NOT_SIGNIFICANT
:value: >
   ('Present not significant',)

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices.PRESENT_NOT_SIGNIFICANT
```

````

````{py:attribute} NOT_RECOGNIZED
:canonical: heat_flow.choices.GenericFlagChoices.NOT_RECOGNIZED
:value: >
   ('not recognized',)

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices.NOT_RECOGNIZED
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.GenericFlagChoices.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.GenericFlagChoices.UNSPECIFIED
```

````

`````

`````{py:class} InSituFlagChoices()
:canonical: heat_flow.choices.InSituFlagChoices

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices.__init__
```

````{py:attribute} CONSIDERED_P
:canonical: heat_flow.choices.InSituFlagChoices.CONSIDERED_P
:value: >
   ('Considered – p',)

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices.CONSIDERED_P
```

````

````{py:attribute} CONSIDERED_T
:canonical: heat_flow.choices.InSituFlagChoices.CONSIDERED_T
:value: >
   ('Considered – T',)

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices.CONSIDERED_T
```

````

````{py:attribute} CONSIDERED_PT
:canonical: heat_flow.choices.InSituFlagChoices.CONSIDERED_PT
:value: >
   ('Considered – pT',)

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices.CONSIDERED_PT
```

````

````{py:attribute} NOT_CONSIDERED
:canonical: heat_flow.choices.InSituFlagChoices.NOT_CONSIDERED
:value: >
   ('not Considered',)

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices.NOT_CONSIDERED
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.InSituFlagChoices.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.InSituFlagChoices.UNSPECIFIED
```

````

`````

`````{py:class} TemperatureFlagChoices()
:canonical: heat_flow.choices.TemperatureFlagChoices

Bases: {py:obj}`django.db.models.TextChoices`

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices.__init__
```

````{py:attribute} TILT_CORRECTED
:canonical: heat_flow.choices.TemperatureFlagChoices.TILT_CORRECTED
:value: >
   ('Tilt corrected',)

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices.TILT_CORRECTED
```

````

````{py:attribute} DRIFT_CORRECTED
:canonical: heat_flow.choices.TemperatureFlagChoices.DRIFT_CORRECTED
:value: >
   ('Drift corrected',)

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices.DRIFT_CORRECTED
```

````

````{py:attribute} NOT_CORRECTED
:canonical: heat_flow.choices.TemperatureFlagChoices.NOT_CORRECTED
:value: >
   ('not corrected',)

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices.NOT_CORRECTED
```

````

````{py:attribute} CORRECTED
:canonical: heat_flow.choices.TemperatureFlagChoices.CORRECTED
:value: >
   ('Corrected (specify)',)

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices.CORRECTED
```

````

````{py:attribute} UNSPECIFIED
:canonical: heat_flow.choices.TemperatureFlagChoices.UNSPECIFIED
:value: >
   ('unspecified',)

```{autodoc2-docstring} heat_flow.choices.TemperatureFlagChoices.UNSPECIFIED
```

````

`````
