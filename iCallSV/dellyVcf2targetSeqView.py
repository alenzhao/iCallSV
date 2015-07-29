'''
Created on Mar 19, 2015
Description: Convert VCF to targetSeqView
#Example:
SampleDesc    Chr1    Start1    End1    LeftSideSegDup    Chr2    Start2    End2    RightSideSeqDup    ValidationStatus    Sample    SplitsSample
Ramos    15    22462315    22462465    TRUE    14    106467050    106467150    TRUE    Failed PCR    1320KB0009MultipleAlnsort.bam    1320KB0009.bam
::Input::
sampleName: Name of the sample that has the structural abberations
sampleBamName: Name of the bam file.
sampleSplitBaName: Name of the split bam file (Use bam file if you dont have split bam file)
vcfFile: Input Delly VCF file for the conversion
outputDir: Directory to write the output file
outputFileName: Name of the output File
::Output::
outputFile: TargetSeqView format text file for a given vcf file.
@author: Ronak H Shah
'''
import vcf
import checkparameters as cp


def Convert2targetSeqView(
        sampleName,
        sampleBamName,
        sampleSplitBamName,
        vcfFile,
        outputDir,
        outputFileName):
    print "Convert2targetSeqView: Will convert vcf to targetSeqVie format\n"
    cp.checkFile(vcfFile)
    cp.checkDir(outputDir)
    print "Convert2targetSeqView: All Input Parameters look good. Lets convert to tab-delimited file\n"
    vcf_reader = vcf.Reader(open(vcfFile, 'r'))
    outputFile = outputDir + "/" + outputFileName
    outputHandle = open(outputFile, "w")
    outputHandle.write(
        "SampleDesc\tChr1\tStart1\tEnd1\tLeftSideSegDup\tChr2\tStart2\tEnd2\tRightSideSeqDup\tValidationStatus\tSample\tSplitsSample\n")
    for record in vcf_reader:
        (chrom1,
         start1,
         start2,
         chrom2,
         contype,
         str1,
         str2) = (None for i in range(7))
        chrom1 = record.CHROM
        start1 = record.POS
        if("END" in record.INFO):
            start2 = record.INFO['END']
        if("CHR2" in record.INFO):
            chrom2 = record.INFO['CHR2']
        if("CT" in record.INFO):
            contype = record.INFO['CT']
        (startCT, endCT) = contype.split("to")
        outputHandle.write(
            sampleName +
            "\t" +
            chrom1 +
            "\t" +
            start1 +
            "\t" +
            start1 +
            "\tFALSE\t" +
            chrom2 +
            "\t" +
            start2 +
            "\t" +
            start2 +
            "\tFALSE\tFailed PCR\t" +
            sampleBamName +
            "\t" +
            sampleSplitBamName)
    outputHandle.close()
    print "Convert2targetSeqView: Finished conversion of Vcf file to targetSeqView file format.\n"
    print "Convert2targetSeqView: Output can be found: ", outputFile, "\n"
    return(outputFile)
#Test module