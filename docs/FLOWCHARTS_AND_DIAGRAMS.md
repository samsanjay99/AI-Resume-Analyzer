# Smart Resume AI - Flowcharts and System Diagrams

## Table of Contents
1. System Architecture Diagrams
2. Analysis Flow Diagrams
3. Algorithm Flowcharts
4. Data Flow Diagrams
5. Component Interaction Diagrams

---

## 1. SYSTEM ARCHITECTURE DIAGRAMS

### 1.1 Overall System Architecture


```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Resume  │ │  Resume  │ │Portfolio │ │   Job    │           │
│  │ Analyzer │ │ Builder  │ │Generator │ │  Search  │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
┌───────┼────────────┼────────────┼────────────┼─────────────────┐
│       │     APPLICATION CONTROLLER LAYER     │                  │
│       ▼            ▼            ▼            ▼                  │
│  ┌─────────────────────────────────────────────────┐           │
│  │         Request Router & Validator               │           │
│  └─────────────────┬───────────────────────────────┘           │
└────────────────────┼───────────────────────────────────────────┘
                     │
┌────────────────────┼───────────────────────────────────────────┐
│                    │    BUSINESS LOGIC LAYER                    │
│    ┌───────────────┴──────────────────┐                        │
│    │                                   │                        │
│    ▼                                   ▼                        │
│ ┌──────────────────┐          ┌──────────────────┐            │
│ │  Smart Analysis  │          │  Deep Analysis   │            │
│ │     Engine       │          │     Engine       │            │
│ │                  │          │                  │            │
│ │ • Fast NLP       │          │ • Advanced NLP   │            │
│ │ • Rule Engine    │          │ • Deep Learning  │            │
│ │ • Heuristics     │          │ • Semantic AI    │            │
│ └────────┬─────────┘          └────────┬─────────┘            │
│          │                              │                       │
│          └──────────────┬───────────────┘                       │
│                         │                                       │
│                         ▼                                       │
│          ┌──────────────────────────────┐                      │
│          │   Common Processing Layer    │                      │
│          │                              │                      │
│          │  • Feature Extraction        │                      │
│          │  • Scoring Engine            │                      │
│          │  • Report Generator          │                      │
│          └──────────────┬───────────────┘                      │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────┼──────────────────────────────────────┐
│                         │    DATA ACCESS LAYER                  │
│                         ▼                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Database │  │  Cache   │  │Knowledge │  │  File    │      │
│  │  Layer   │  │  Layer   │  │   Base   │  │ Storage  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Analysis Engine Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE CORE                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Input Processing Module                   │    │
│  │  • Document Parser  • Text Extractor  • Validator  │    │
│  └──────────────────────┬─────────────────────────────┘    │
│                         │                                   │
│                         ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │              NLP Pipeline                           │    │
│  │                                                     │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │    │
│  │  │Tokenizer │→ │  NER     │→ │ Semantic │        │    │
│  │  │          │  │ Engine   │  │ Analyzer │        │    │
│  │  └──────────┘  └──────────┘  └──────────┘        │    │
│  └──────────────────────┬─────────────────────────────┘    │
│                         │                                   │
│           ┌─────────────┴─────────────┐                    │
│           │                           │                    │
│           ▼                           ▼                    │
│  ┌─────────────────┐        ┌─────────────────┐          │
│  │ Smart Analysis  │        │ Deep Analysis   │          │
│  │                 │        │                 │          │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │          │
│  │ │ TF-IDF      │ │        │ │Transformers │ │          │
│  │ │ Vectorizer  │ │        │ │   Model     │ │          │
│  │ └─────────────┘ │        │ └─────────────┘ │          │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │          │
│  │ │ Rule-based  │ │        │ │ Attention   │ │          │
│  │ │   Engine    │ │        │ │ Mechanism   │ │          │
│  │ └─────────────┘ │        │ └─────────────┘ │          │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │          │
│  │ │ Heuristic   │ │        │ │ Reasoning   │ │          │
│  │ │  Matcher    │ │        │ │   Engine    │ │          │
│  │ └─────────────┘ │        │ └─────────────┘ │          │
│  └────────┬────────┘        └────────┬────────┘          │
│           │                          │                    │
│           └──────────┬───────────────┘                    │
│                      │                                    │
│                      ▼                                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │            Scoring & Evaluation Module             │  │
│  │                                                     │  │
│  │  • ATS Score Calculator                            │  │
│  │  • Keyword Match Scorer                            │  │
│  │  • Quality Assessment Engine                       │  │
│  │  • Confidence Estimator                            │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │          Report Generation Module                   │  │
│  │                                                     │  │
│  │  • Insight Generator  • PDF Builder  • Visualizer  │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 2. ANALYSIS FLOW DIAGRAMS

### 2.1 Smart Analysis Flow

```
START
  │
  ▼
┌─────────────────┐
│ Upload Resume   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate File   │
│ • Format check  │
│ • Size check    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Text    │
│ • PDF Parser    │
│ • DOCX Parser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Preprocessing   │
│ • Clean text    │
│ • Tokenize      │
│ • Normalize     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Extract │
│ • TF-IDF        │
│ • Keywords      │
│ • Entities      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Apply Rules     │
│ • Pattern match │
│ • Heuristics    │
│ • Weights       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate Score │
│ • ATS: 30%      │
│ • Keywords: 35% │
│ • Structure: 20%│
│ • Complete: 15% │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Report │
│ • Scores        │
│ • Insights      │
│ • Suggestions   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Results │
└─────────────────┘
  │
  ▼
END
```

### 2.2 Deep Analysis Flow

```
START
  │
  ▼
┌─────────────────┐
│ Upload Resume   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate & Parse│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Advanced NLP    │
│ • Tokenization  │
│ • POS Tagging   │
│ • Dependency    │
│ • NER           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic        │
│ Embedding       │
│ • 768-dim       │
│ • Contextual    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Multi-Layer     │
│ Analysis        │
│                 │
│ Layer 1: ───────┤
│ Structure       │
│                 │
│ Layer 2: ───────┤
│ Content Quality │
│                 │
│ Layer 3: ───────┤
│ Role Fit        │
│                 │
│ Layer 4: ───────┤
│ Career Path     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Attention       │
│ Mechanism       │
│ • Context       │
│ • Relationships │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reasoning       │
│ Engine          │
│ • Logic rules   │
│ • Inference     │
│ • Confidence    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Comprehensive   │
│ Scoring         │
│ • Multiple      │
│   factors       │
│ • Weighted sum  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detailed Report │
│ • Deep insights │
│ • Skill gaps    │
│ • Roadmap       │
│ • Resources     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PDF Generation  │
│ • Charts        │
│ • Visualizations│
└────────┬────────┘
         │
         ▼
END
```

## 3. ALGORITHM FLOWCHARTS

### 3.1 ATS Score Calculation Algorithm

```
START
  │
  ▼
┌──────────────────────┐
│ Input: resume_text   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Initialize scores    │
│ format_score = 0     │
│ keyword_score = 0    │
│ structure_score = 0  │
│ readability_score = 0│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Check Format         │
│ • Is parseable?      │
│ • Has tables?        │
│ • Has images?        │
└──────────┬───────────┘
           │
           ▼
     ┌─────┴─────┐
     │ Parseable?│
     └─────┬─────┘
      Yes  │  No
     ┌─────┴─────┐
     │           │
     ▼           ▼
format_score  format_score
   += 25         += 0
     │           │
     └─────┬─────┘
           │
           ▼
┌──────────────────────┐
│ Extract Keywords     │
│ • Job-specific       │
│ • Technical skills   │
│ • Soft skills        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Calculate Keyword    │
│ Density              │
│ density = matches/   │
│           total      │
└──────────┬───────────┘
           │
           ▼
keyword_score = 
  density * 30
           │
           ▼
┌──────────────────────┐
│ Analyze Structure    │
│ • Has sections?      │
│ • Proper order?      │
│ • Clear headings?    │
└──────────┬───────────┘
           │
           ▼
structure_score = 
  section_quality * 20
           │
           ▼
┌──────────────────────┐
│ Calculate            │
│ Readability          │
│ • Flesch score       │
│ • Sentence length    │
└──────────┬───────────┘
           │
           ▼
readability_score = 
  flesch_score * 0.15
           │
           ▼
┌──────────────────────┐
│ Total ATS Score =    │
│ format_score +       │
│ keyword_score +      │
│ structure_score +    │
│ readability_score    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Normalize to 0-100   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Return ATS Score     │
└──────────────────────┘
  │
  ▼
END
```

### 3.2 Skill Gap Analysis Algorithm

```
START
  │
  ▼
┌──────────────────────┐
│ Input:               │
│ • current_skills     │
│ • required_skills    │
│ • job_role           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ missing_skills =     │
│ required - current   │
└──────────┬───────────┘
           │
           ▼
     ┌─────┴─────┐
     │ missing   │
     │ empty?    │
     └─────┬─────┘
      Yes  │  No
     ┌─────┴─────┐
     │           │
     ▼           ▼
  Return      Continue
  "No gaps"      │
                 ▼
┌──────────────────────┐
│ For each missing     │
│ skill:               │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Calculate Priority   │
│ • Role importance    │
│ • Market demand      │
│ • Learning curve     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ priority_score =     │
│ (importance * 0.4) + │
│ (demand * 0.3) +     │
│ (1/difficulty * 0.3) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Find Related Skills  │
│ in current_skills    │
└──────────┬───────────┘
           │
           ▼
     ┌─────┴─────┐
     │ Has       │
     │ related?  │
     └─────┬─────┘
      Yes  │  No
     ┌─────┴─────┐
     │           │
     ▼           ▼
learning_time  learning_time
  = base/2      = base
     │           │
     └─────┬─────┘
           │
           ▼
┌──────────────────────┐
│ Recommend Resources  │
│ • Online courses     │
│ • Books              │
│ • Practice projects  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Add to gap_report    │
└──────────┬───────────┘
           │
           ▼
     ┌─────┴─────┐
     │ More      │
     │ skills?   │
     └─────┬─────┘
      Yes  │  No
     ┌─────┴─────┐
     │           │
     ▼           ▼
   Loop       Continue
   back          │
                 ▼
┌──────────────────────┐
│ Sort by priority     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Generate Roadmap     │
│ • Short-term (1-3mo) │
│ • Mid-term (3-6mo)   │
│ • Long-term (6-12mo) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Return gap_report    │
└──────────────────────┘
  │
  ▼
END
```

## 4. DATA FLOW DIAGRAMS

### 4.1 Resume Analysis Data Flow

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. Upload Resume
     ▼
┌──────────────┐
│   Web UI     │
└────┬─────────┘
     │ 2. File + Metadata
     ▼
┌──────────────┐
│  Controller  │
└────┬─────────┘
     │ 3. Validate & Route
     ▼
┌──────────────┐
│   Parser     │
└────┬─────────┘
     │ 4. Raw Text
     ▼
┌──────────────┐
│ NLP Pipeline │
└────┬─────────┘
     │ 5. Tokens + Entities
     ▼
┌──────────────┐
│   Analysis   │
│   Engine     │
└────┬─────────┘
     │ 6. Features
     ▼
┌──────────────┐
│   Scoring    │
│   Module     │
└────┬─────────┘
     │ 7. Scores
     ▼
┌──────────────┐
│   Report     │
│  Generator   │
└────┬─────────┘
     │ 8. Report Data
     ▼
┌──────────────┐
│   Database   │
└────┬─────────┘
     │ 9. Stored
     ▼
┌──────────────┐
│   Web UI     │
└────┬─────────┘
     │ 10. Display
     ▼
┌──────────┐
│  User    │
└──────────┘
```

### 4.2 Portfolio Generation Data Flow

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. Resume Data
     ▼
┌──────────────┐
│ Portfolio    │
│ Generator    │
└────┬─────────┘
     │ 2. Parse Data
     ▼
┌──────────────┐
│  Content     │
│  Mapper      │
└────┬─────────┘
     │ 3. Mapped Sections
     ▼
┌──────────────┐
│  Template    │
│  Engine      │
└────┬─────────┘
     │ 4. HTML Template
     ▼
┌──────────────┐
│  Style       │
│  Processor   │
└────┬─────────┘
     │ 5. Styled HTML
     ▼
┌──────────────┐
│  Asset       │
│  Manager     │
└────┬─────────┘
     │ 6. Complete Portfolio
     ▼
┌──────────────┐
│  File        │
│  Storage     │
└────┬─────────┘
     │ 7. Download Link
     ▼
┌──────────┐
│  User    │
└──────────┘
```

## 5. COMPONENT INTERACTION DIAGRAMS

### 5.1 Resume Builder Interaction

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│  User   │         │   UI    │         │ Builder │
└────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │
     │ Enter Info        │                   │
     ├──────────────────>│                   │
     │                   │                   │
     │                   │ Validate          │
     │                   ├──────────────────>│
     │                   │                   │
     │                   │ Validation OK     │
     │                   │<──────────────────┤
     │                   │                   │
     │ Select Template   │                   │
     ├──────────────────>│                   │
     │                   │                   │
     │                   │ Generate Resume   │
     │                   ├──────────────────>│
     │                   │                   │
     │                   │                   │ ┌──────────┐
     │                   │                   ├>│ Template │
     │                   │                   │ │  Engine  │
     │                   │                   │<┤          │
     │                   │                   │ └──────────┘
     │                   │                   │
     │                   │                   │ ┌──────────┐
     │                   │                   ├>│   PDF    │
     │                   │                   │ │ Generator│
     │                   │                   │<┤          │
     │                   │                   │ └──────────┘
     │                   │                   │
     │                   │ Resume PDF        │
     │                   │<──────────────────┤
     │                   │                   │
     │ Download          │                   │
     │<──────────────────┤                   │
     │                   │                   │
```

### 5.2 Job Recommendation Interaction

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  User   │    │Recommend│    │ Matcher │    │   Job   │
│ Profile │    │ Engine  │    │ Service │    │   DB    │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │
     │ Get Jobs     │              │              │
     ├─────────────>│              │              │
     │              │              │              │
     │              │ Fetch Jobs   │              │
     │              ├─────────────────────────────>│
     │              │              │              │
     │              │ Job Listings │              │
     │              │<─────────────────────────────┤
     │              │              │              │
     │              │ Calculate    │              │
     │              │ Match Scores │              │
     │              ├─────────────>│              │
     │              │              │              │
     │              │              │ ┌──────────┐ │
     │              │              ├>│  Skill   │ │
     │              │              │ │ Matcher  │ │
     │              │              │<┤          │ │
     │              │              │ └──────────┘ │
     │              │              │              │
     │              │              │ ┌──────────┐ │
     │              │              ├>│Experience│ │
     │              │              │ │ Matcher  │ │
     │              │              │<┤          │ │
     │              │              │ └──────────┘ │
     │              │              │              │
     │              │ Ranked Jobs  │              │
     │              │<─────────────┤              │
     │              │              │              │
     │ Job List     │              │              │
     │<─────────────┤              │              │
     │              │              │              │
```

---

## 6. PROCESSING PIPELINE DIAGRAMS

### 6.1 Text Processing Pipeline

```
Input Text
    │
    ▼
┌─────────────────┐
│ Text Cleaning   │
│ • Remove noise  │
│ • Fix encoding  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Tokenization    │
│ • Word tokens   │
│ • Sentence split│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Normalization   │
│ • Lowercase     │
│ • Lemmatization │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stop Word       │
│ Removal         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ POS Tagging     │
│ • Noun, Verb    │
│ • Adjective     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Named Entity    │
│ Recognition     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature         │
│ Extraction      │
└────────┬────────┘
         │
         ▼
    Processed
    Features
```

### 6.2 Scoring Pipeline

```
Features
    │
    ▼
┌─────────────────┐
│ ATS Score       │
│ Calculator      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Keyword Match   │
│ Scorer          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Structure       │
│ Analyzer        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Quality         │
│ Assessor        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Weight          │
│ Application     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Score           │
│ Normalization   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Confidence      │
│ Calculation     │
└────────┬────────┘
         │
         ▼
    Final Scores
```

---

**Document Version**: 1.0  
**Last Updated**: February 2026
