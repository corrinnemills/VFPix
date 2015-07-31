import FWCore.ParameterSet.Config as cms
import sys
import math

###########################################################
##### Set up process #####
###########################################################

process = cms.Process ('VFPIX')
process.load ('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet (
  input = cms.untracked.int32 (-1)
)
process.source = cms.Source ('PoolSource',
  fileNames = cms.untracked.vstring ("file:T3/FullContent_VBFHToTauTau_trkExt_skimmed.root")
)

process.load("CondCore.DBCommon.CondDBCommon_cfi")
from CondCore.DBCommon.CondDBSetup_cfi import *
process.jec = cms.ESSource("PoolDBESSource",
      DBParameters = cms.PSet(
        messageLevel = cms.untracked.int32(0)
        ),
      timetype = cms.string('runnumber'),
      toGet = cms.VPSet(
      cms.PSet(
            record = cms.string('JetCorrectionsRecord'),
            tag    = cms.string('JetCorrectorParametersCollection_PhaseII_HGCal140PU_AK4PFchs'),
            label  = cms.untracked.string('AK4PFchs')
            ),
      ## here you add as many jet types as you need
      ## note that the tag name is specific for the particular sqlite file 
      ), 
      connect = cms.string('sqlite:PhaseII_HGCal140PU.db')
)
## add an es_prefer statement to resolve a possible conflict from simultaneous connection to a global tag
process.es_prefer_jec = cms.ESPrefer('PoolDBESSource','jec')

process.load("JetMETCorrections.Configuration.JetCorrectionServices_cff")
process.load("JetMETCorrections.Configuration.JetCorrectionServicesAllAlgos_cff")
process.ak4PFCHSL1Fastjet = cms.ESProducer("L1FastjetCorrectionESProducer",
    srcRho = cms.InputTag("kt6PFJets","rho"),
    algorithm = cms.string('AK4PFchs'),
    level = cms.string('L1FastJet')
)
process.ak4PFCHSL2Relative = cms.ESProducer("LXXXCorrectionESProducer",
    algorithm = cms.string('AK4PFchs'),
    level = cms.string('L2Relative')
)
process.ak4PFCHSL3Absolute = cms.ESProducer("LXXXCorrectionESProducer",
    algorithm = cms.string('AK4PFchs'),
    level = cms.string('L3Absolute')
)
process.ak4PFCHSL1FastL2L3 = cms.ESProducer("JetCorrectionESChain",
    correctors = cms.vstring('ak4PFCHSL1Fastjet', 
        'ak4PFCHSL2Relative', 
        'ak4PFCHSL3Absolute')
)
process.ak4PFCHSJetsL1FastL2L3   = cms.EDProducer('PFJetCorrectionProducer',
    src         = cms.InputTag('ak4PFJetsCHS'),
    correctors  = cms.vstring('ak4PFCHSL1FastL2L3')
)

process.VBFQuarkProducer = cms.EDProducer ('VBFQuarkProducer',
  genParticles = cms.InputTag ("genParticles", ""),
  jets = cms.InputTag ("ak4PFCHSJetsL1FastL2L3", ""),
  tracks = cms.InputTag ("generalTracks", ""),
)

process.PoolOutputModule = cms.OutputModule ("PoolOutputModule",
  splitLevel = cms.untracked.int32 (0),
  eventAutoFlushCompressedSize = cms.untracked.int32 (5242880),
  fileName = cms.untracked.string ("/afs/cern.ch/user/a/ahart/T3/FullContent_VBFHToTauTau_trkExt_skimmed.root"),
  outputCommands = cms.untracked.vstring (
    'keep *',
  ),
  dropMetaData = cms.untracked.string ("ALL")
)

process.myPath = cms.Path (process.ak4PFCHSJetsL1FastL2L3*process.VBFQuarkProducer)
process.myEndPath = cms.EndPath (process.PoolOutputModule)
