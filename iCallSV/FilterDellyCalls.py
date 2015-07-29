'''
Created on Mar 17, 2015
Description: This module will filter calls made by Delly which are in a VCF format
@author: Ronak H Shah
'''
'''
::Inputs::
inputVcf: Input VCF file name with path
outputVcf: Output VCF file name.
outputDir: Output directory
controlId: Control Sample ID (Should be part of Sample Name in VCF)
caseID: Case Sample ID (Should be part of Sample Name in VCF)
hospotFile: List of Genes that have Hotspot Structural Variants (Tab-delimited Format without header:chr    start    end    geneName).
peSupport: overall pair-end read support threshold for the event
srSupport: overall split-reads support threshold for the event
peSupportHotspot: overall pair-end read support threshold for the event in hot-spot region
srSupportHotspot: overall split-reads support threshold for the event in hot-spot region
peSupportCase: pair-end read support threshold for the event in the Case sample
srSupportCase: split-reads support threshold for the event in the Case sample
peSupportHotspotCase: pair-end read support threshold for the event in hot-spot region for the Case sample
srSupportHotspotCase: split-reads support threshold for the event in hot-spot region for the Case sample
peSupportControl: pair-end read support threshold for the event in the Control sample
srSupportControl: split-reads support threshold for the event in the Control sample
peSupportHotspotControl: pair-end read support threshold for the event in hot-spot region for the Control sample
srSupportHotspotControl: split-reads support threshold for the event in hot-spot region for the Control sample
svlength: length of the structural variants
mapq: overall mapping quality
mapqHotspot: mapping quality for hot-spots

::Output::
Filtered VCF files
'''
import os
import sys
import vcf
import re
import checkparameters as cp
import checkHotSpotList as chl


def FilterVCF(
        inputVcf,
        outputVcf,
        outputDir,
        controlId,
        caseID,
        hotspotFile,
        svlength,
        mapq,
        mapqHotspot,
        peSupport,
        srSupport,
        peSupportHotspot,
        srSupportHotspot,
        peSupportCase,
        srSupportCase,
        peSupportHotspotCase,
        srSupportHotspotCase,
        peSupportControl,
        srSupportControl,
        peSupportHotspotControl,
        srSupportHotspotControl):
    print "FilterDellyCalls: We will now check all the input parameters.\n"
    # Check input parameters
    cp.checkDir(outputDir)
    cp.checkFile(inputVcf)
    cp.checkFile(hotspotFile)
    cp.checkEmpty(controlId, "Control Bam ID")
    cp.checkEmpty(caseID, "Case Bam ID")
    cp.checkInt(svlength, "Length of Structural Variant Threshold")
    cp.checkInt(mapq, "Mapping quality of Reads threshold")
    cp.checkInt(mapqHotspot, "Mapping quality of Reads threshold for hotspot events ")
    cp.checkInt(peSupport, "overall pair-end read support threshold for the event")
    cp.checkInt(srSupport, "overall split-reads support threshold for the event")
    cp.checkInt(
        peSupportHotspot,
        "overall pair-end read support threshold for the event in hot-spot region")
    cp.checkInt(
        srSupportHotspot,
        "overall split-reads support threshold for the event in hot-spot region")
    cp.checkInt(
        peSupportCase,
        "overall pair-end read support threshold for the event for the Case sample")
    cp.checkInt(
        srSupportCase,
        "overall split-reads support threshold for the event for the Case sample")
    cp.checkInt(
        peSupportHotspotCase,
        "overall pair-end read support threshold for the event in hot-spot region for the Case sample")
    cp.checkInt(
        srSupportHotspotCase,
        "overall split-reads support threshold for the event in hot-spot region for the Case sample")
    cp.checkInt(
        peSupportControl,
        "overall pair-end read support threshold for the event for the Control sample")
    cp.checkInt(
        srSupportControl,
        "overall split-reads support threshold for the event for the Control sample")
    cp.checkInt(
        peSupportHotspotControl,
        "overall pair-end read support threshold for the event in hot-spot region for the Control sample")
    cp.checkInt(
        srSupportHotspotControl,
        "overall split-reads support threshold for the event in hot-spot region for the Control sample")
    print "FilterDellyCalls: All Input Parameters look good for filtering these VCF file.\n"
    print "FilterDellyCalls: We will filter the given VCF file now.\n"
    # Make a string of all the variables
    thresholdVariablesList = [svlength,
                              mapq,
                              mapqHotspot,
                              peSupport,
                              srSupport,
                              peSupportHotspot,
                              srSupportHotspot,
                              peSupportCase,
                              srSupportCase,
                              peSupportHotspotCase,
                              srSupportHotspotCase,
                              peSupportControl,
                              srSupportControl,
                              peSupportHotspotControl,
                              srSupportHotspotControl]
    thresholdVariables = ",".join(str(v) for v in thresholdVariablesList)

    hotspotDict = chl.ReadHotSpotFile(hotspotFile)
    vcf_reader = vcf.Reader(open(inputVcf, 'r'))
    outputFile = outputDir + "/" + outputVcf
    vcf_writer = vcf.Writer(open(outputFile, 'w'), vcf_reader)
    samples = vcf_reader.samples
    pattern = re.compile(caseID)
    # Get the case and control id
    caseIDinVcf = None
    controlIDinVcf = None
    for sample in samples:
        match = re.search(pattern, sample)
        if(match):
            caseIDinVcf = sample
        else:
            controlIDinVcf = sample
    #
    for record in vcf_reader:
        # Define all variables:
        (chrom1,
         start1,
         start2,
         chrom2,
         filter,
         svlengthFromDelly,
         mapqFromDelly,
         svtype,
         peSupportFromDelly,
         srSupportFromDelly,
         contype,
         caseDV,
         caseRV,
         caseFT,
         controlDV,
         controlRV,
         controlFT) = (None for i in range(17))
        chrom1 = record.CHROM
        start1 = record.POS
        filter = record.FILTER
        if("END" in record.INFO):
            start2 = record.INFO['END']
        if("CHR2" in record.INFO):
            chrom2 = record.INFO['CHR2']
        if("SVLEN" in record.INFO):
            svlengthFromDelly = record.INFO['SVLEN']
        else:
            svlengthFromDelly = abs(start2 - start1)
        if("MAPQ" in record.INFO):
            mapqFromDelly = record.INFO['MAPQ']
        if("SVTYPE" in record.INFO):
            svtype = record.INFO['SVTYPE']
        if("PE" in record.INFO):
            peSupportFromDelly = record.INFO['PE']
        if("SR" in record.INFO):
            srSupportFromDelly = record.INFO['SR']
        if("CT" in record.INFO):
            contype = record.INFO['CT']
        caseCalls = record.genotype(caseIDinVcf)
        controlCalls = record.genotype(controlIDinVcf)
        if(hasattr(caseCalls.data, "FT")):
            caseFT = caseCalls.data.FT
        if(hasattr(caseCalls.data, "DV")):
            caseDV = caseCalls.data.DV
        if(hasattr(caseCalls.data, "RV")):
            caseRV = caseCalls.data.RV

        if(hasattr(controlCalls.data, "FT")):
            controlFT = controlCalls.data.FT
        if(hasattr(controlCalls.data, "DV")):
            controlDV = controlCalls.data.DV
        if(hasattr(controlCalls.data, "RV")):
            controlRV = controlCalls.data.RV
        # Make a string of all the variables
        dellyVariablesList = [chrom1,
                              start1,
                              start2,
                              chrom2,
                              filter,
                              svlengthFromDelly,
                              mapqFromDelly,
                              svtype,
                              peSupportFromDelly,
                              srSupportFromDelly,
                              contype,
                              caseFT,
                              caseDV,
                              caseRV,
                              controlFT,
                              controlDV,
                              controlRV]
        dellyVariables = ",".join(str(v) for v in dellyVariablesList)
        # print chrom1, start1, start2, chrom2, svlengthFromDelly, mapqFromDelly,
        # svtype, peSupportFromDelly, srSupportFromDelly, contype, caseDV, caseRV,
        # controlDV, controlRV
        filterFlag = GetFilteredRecords(dellyVariables, thresholdVariables, hotspotDict)
        if(filterFlag):
            vcf_writer.write_record(record)
    vcf_writer.close()
    print "FilterDellyCalls: We have finished filtering: ", inputVcf, " file.\n"
    print "FilterFellyCalls: Output hass been written in: ", outputFile, " file.\n"
    return(outputFile)


def GetFilteredRecords(dellyVarialbles, thresholdVariables, hotspotDict):
    (svlength,
     mapq,
     mapqHotspot,
     peSupport,
     srSupport,
     peSupportHotspot,
     srSupportHotspot,
     peSupportCase,
     srSupportCase,
     peSupportHotspotCase,
     srSupportHotspotCase,
     peSupportControl,
     srSupportControl,
     peSupportHotspotControl,
     srSupportHotspotControl) = thresholdVariables.split(",")
    (chrom1,
     start1,
     start2,
     chrom2,
     filter,
     svlengthFromDelly,
     mapqFromDelly,
     svtype,
     peSupportFromDelly,
     srSupportFromDelly,
     contype,
     caseFT,
     caseDV,
     caseRV,
     controlFT,
     controlDV,
     controlRV) = dellyVarialbles.split(",")
    # Get if its a hotspot or not
    hotspotTag = chl.CheckIfItIsHotspot(chrom1, start1, chrom2, start2, hotspotDict)
    filterFlag = False
    if(hotspotTag):
        if(filter == "PASS" and controlFT == "LowQual"):
            if(svlengthFromDelly != "None"):
                if(int(svlengthFromDelly) >= int(svlength)):
                    filterFlag = True
                else:
                    filterFlag = False
            else:
                filterFlag = True
        if(not filterFlag):
            if(svlengthFromDelly != "None"):
                if((int(svlengthFromDelly) >= int(svlength)) and (int(mapqFromDelly) >= int(mapqHotspot)) and (int(peSupportFromDelly) >= int(peSupportHotspot)) and (int(caseDV) > int(peSupportHotspotCase)) and (int(controlDV) <= int(peSupportHotspotControl))):
                    if(srSupportFromDelly != "None"):
                        if((int(srSupportFromDelly) >= int(srSupportHotspot)) and (int(caseRV) >= int(srSupportHotspotCase)) and (int(controlRV) <= int(srSupportHotspotControl))):
                            filterFlag = True
                        else:
                            filterFlag = False
                    else:
                        filterFlag = True
                else:
                    filterFlag = False
            else:
                if((int(mapqFromDelly) >= int(mapqHotspot)) and (int(peSupportFromDelly) >= int(peSupportHotspot)) and (int(caseDV) >= int(peSupportHotspotCase)) and (int(controlDV) <= int(peSupportHotspotControl))):
                    if(srSupportFromDelly != "None"):
                        if((int(srSupportFromDelly) >= int(srSupportHotspot)) and (int(caseRV) >= int(srSupportHotspotCase)) and (int(controlRV) <= int(srSupportHotspotControl))):
                            filterFlag = True
                        else:
                            filterFlag = False
                    else:
                        filterFlag = True
                else:
                    filterFlag = False
    else:
        if(svlengthFromDelly != "None"):
            # print svlengthFromDelly, svlength, mapqFromDelly, mapq,
            # peSupportFromDelly, peSupport, caseDV, peSupportCase, controlDV,
            # peSupportControl
            if((int(svlengthFromDelly) >= int(svlength)) and (int(mapqFromDelly) >= int(mapq)) and (int(peSupportFromDelly) >= int(peSupport)) and (int(caseDV) >= int(peSupportCase)) and (int(controlDV) <= int(peSupportControl))):
                if(srSupportFromDelly != "None"):
                    if((int(srSupportFromDelly) >= int(srSupport)) and (int(caseRV) >= int(srSupportCase)) and (int(controlRV) <= int(srSupportControl))):
                        filterFlag = True
                    else:
                        filterFlag = False
                else:
                    filterFlag = True
            else:
                filterFlag = False
        else:
            if((int(mapqFromDelly) >= int(mapq)) and (int(peSupportFromDelly) >= int(peSupport)) and (int(caseDV) >= int(peSupportCase)) and (int(controlDV) <= int(peSupportControl))):
                if(srSupportFromDelly != "None"):
                    if((int(srSupportFromDelly) >= int(srSupport)) and (int(caseRV) >= int(srSupportCase)) and (int(controlRV) <= int(srSupportControl))):
                        filterFlag = True
                    else:
                        filterFlag = False
                else:
                    filterFlag = True
            else:
                filterFlag = False

    return(filterFlag)


# # Test the module
# FilterVCF(
#     inputVcf="/dmp/hot/shahr2/IMPACT/Test/SVtest/35462375-T_bc44_jmp.vcf",
#     outputVcf="35462375-T_bc44_jmp.stdfilter.vcf",
#     outputDir="/dmp/hot/shahr2/IMPACT/Test/SVtest/",
#     controlId="35462375-N",
#     caseID="35462375-T",
#     hotspotFile="/home/shahr2/workspace/dmp-data/mskdata/interval-lists/structuralvariants_geneInterval.txt",
#     svlength=500,
#     mapq=20,
#     mapqHotspot=5,
#     peSupport=5,
#     srSupport=0,
#     peSupportHotspot=3,
#     srSupportHotspot=0,
#     peSupportCase=2,
#     srSupportCase=0,
#     peSupportHotspotCase=1,
#     srSupportHotspotCase=0,
#     peSupportControl=5,
#     srSupportControl=5,
#     peSupportHotspotControl=5,
#     srSupportHotspotControl=5)