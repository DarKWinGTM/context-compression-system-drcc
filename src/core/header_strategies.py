"""
Header Generation Strategies
=============================

Strategy Pattern implementations for different header generation modes.
Each strategy handles a specific header type and compression mode.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
# PHASE 11: Import from renamed modules
from .header_config import HeaderConfig, HeaderStatistics


class HeaderStrategy(ABC):
    """
    Abstract base class for header generation strategies.

    Subclasses must implement:
    - generate(): Create header based on config
    - validate(): Verify header format
    """

    @abstractmethod
    def generate(self, config: HeaderConfig) -> str:
        """
        Generate header based on configuration

        Args:
            config: HeaderConfig object with strategy parameters

        Returns:
            Generated header string
        """
        pass

    @abstractmethod
    def validate(self, header: str) -> bool:
        """
        Validate generated header format

        Args:
            header: Header string to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def get_metadata(self) -> Dict[str, str]:
        """Get strategy metadata"""
        return {
            'strategy': self.__class__.__name__,
            'version': '1.0',
            'description': self.__doc__ or ''
        }


class NormalModeStrategy(HeaderStrategy):
    """
    Full dictionary + complete decompression instructions.

    Generates complete headers with all dictionary tables
    and detailed decompression instructions for AI systems.
    """

    def generate(self, config: HeaderConfig) -> str:
        """Generate full header with all dictionaries"""
        if config.dictionary_set == '1599':
            return self._build_normal_header_1599(config)
        elif config.dictionary_set == '2000':
            return self._build_normal_header_2000(config)
        else:
            return self._build_normal_header_default(config)

    def validate(self, header: str) -> bool:
        """Check header contains required decompression instructions"""
        required_patterns = [
            'DECOMPRESSION INSTRUCTIONS',
            'Dictionary',
            'Template',
        ]
        return all(pattern in header for pattern in required_patterns)

    def _build_normal_header_1599(self, config: HeaderConfig) -> str:
        """
        Build 1599-word dictionary header with FULL DICTIONARIES.

        PHASE 11 FIX: Now builds dictionaries dynamically from actual compressed content
        instead of using hard-coded values. This ensures headers match the compression.
        """
        # PHASE 11: Check if actual dictionaries are provided
        dictionaries = config.metadata.get('dictionaries')

        if dictionaries:
            # Use actual dictionaries from compressed content
            template_dict = dictionaries.get('template_dict', {})
            phrase_dict = dictionaries.get('phrase_dict', {})
            word_dict = dictionaries.get('word_dict', {})

            # Build template table from actual dicts
            template_lines = [f"{k}={v}" for k, v in sorted(template_dict.items())]
            template_table = '\n'.join(template_lines)

            # Build phrase table from actual dicts
            phrase_entries = [f"{k}={v}" for k, v in sorted(phrase_dict.items())]
            phrase_table = '|'.join(phrase_entries)

            # Build word table from actual dicts
            word_entries = [f"{k}={v}" for k, v in sorted(word_dict.items())]
            word_table = '|'.join(word_entries)

            template_count = len(template_dict)
            phrase_count = len(phrase_dict)
            word_count = len(word_dict)
        else:
            # Fallback to hard-coded dictionaries (backward compatibility)
            template_table = """T1=**📜 Constitutional Basis:**
T2=#### **📜 Constitutional Basis:**
T3=**📊 Implementation Standards:**
T4=#### **📊 Implementation Standards:**
T5=#### **🏗️ Quality Metrics:**
T6=**🏗️ Quality Metrics:**
T7=- **Success Indicators**:
T8=#### **🧠 Visual Framework:**
T9=**🧠 Visual Framework:**
T10=#### **💡 Practical Examples:**
T11=**💡 Practical Examples:**
T12=**🎯 Core Framework:**
T13=#### **🎯 Core Framework:**
T14=**🎯 Purpose & Usage:**
T15=#### **🎯 Core Verification Framework:**
T16=**🎯 Core Verification Framework:**
T17=- **Learning Integration**:
T18=- **Constitutional Compliance**:
T19=- **Configuration Management**:"""

            phrase_table = "€a=constitutional basis|€aa=traac adaptive reasoning framework|€ab=tumix constitutional multi|€ac=agent framework|€ad=rot constitutional thought graph system|€ae=quality control|€af=usage guidelines|€ag=mandatory requirements|€ah=user authority preservation|€ai=perspective analysis|€aj=principle evolution|€ak=constitutional foundation|€al=md absolute authority principle|€am=communication framework|€an=functional intent verification|€ao=awcloud system architecture|€ap=modal system architecture|€aq=development standards|€ar=verification framework|€as=depth calibration|€at=domain synthesis|€au=system integration|€av=constitutional compliance protocol|€aw=efficiency metrics|€ax=mandatory agents|€ay=perspective coverage|€az=accuracy improvement|€b=success indicators|€ba=systematic analysis|€bb=all previous principles|€bc=implementation examples|€bd=implementation feasibility|€be=security specialist|€bf=information integrity|€bg=internet verification|€bh=cognitive validation|€bi=complexity assessment|€c=quality metrics|€d=implementation standards|€e=visual framework|€f=constitutional compliance|€g=practical examples|€h=apply principle|€i=zero hallucination policy|€j=quality assurance|€k=level reasoning|€l=reference validation|€m=zero hallucination|€n=based systematic analysis|€o=document consistency|€p=continuous improvement|€q=technical domain expertise|€r=implementation methodology|€s=success patterns|€t=token reduction|€u=learning integration|€v=pattern recognition|€w=faster processing|€x=all core working principles|€y=core working principles|€z=cognitive chunking"

            word_table = "$#=CLAUDE.md|$A=user|$B=constitutional|$C=framework|$D=principle|$E=verification|$F=integration|$G=multi|$H=authority|$I=analysis|$J=core|$K=system|$L=validation|$M=template|$N=quality|$O=implementation|$P=metrics|$Q=security|$R=principles|$S=performance|$T=this|$U=domain|$V=technical|$W=traac|$X=article|$Y=reasoning|$Z=context|฿a=with|฿aa=complex|฿ab=expertise|฿ac=process|฿ad=expert|฿ae=appendix|฿af=working|฿ag=architecture|฿ah=systematic|฿ai=improvement|฿aj=learning|฿ak=pattern|฿al=step|฿am=real|฿an=agents|฿ao=reality|฿ap=management|฿aq=protocol|฿ar=must|฿as=collaboration|฿at=depth|฿au=efficiency|฿av=decision|฿aw=requirements|฿ax=indicators|฿ay=only|฿az=rate|฿b=part|฿ba=level|฿bb=drcc|฿bc=accuracy|฿bd=cognitive|฿be=task|฿bf=before|฿bg=perspective|฿bh=examples|฿bi=solution|฿bj=assessment|฿bk=reuse|฿bl=faster|฿bm=documentation|฿bn=protocols|฿bo=code|฿bp=activation|฿bq=templates|฿br=token|฿bs=apply|฿bt=mandatory|฿bu=policy|฿bv=continuous|฿bw=first|฿bx=from|฿by=systems|฿bz=verified|฿c=zero|฿ca=identity|฿cb=consistency|฿cc=synthesis|฿cd=purpose|฿ce=content|฿cf=practical|฿cg=internet|฿ch=requirement|฿ci=reduction|฿cj=thai|฿ck=detection|฿cl=self|฿cm=compression|฿cn=without|฿co=information|฿cp=project|฿cq=anti|฿cr=modal|฿cs=specific|฿ct=mapping|฿cu=expiration|฿cv=approach|฿cw=feedback|฿cx=clear|฿cy=problems|฿cz=example|฿d=patterns|฿da=read|฿db=solutions|฿dc=files|฿dd=thought|฿de=emergency|฿df=gitbook|฿dg=method|฿dh=critical|฿di=effectiveness|฿dj=comprehensive|฿dk=knowledge|฿dl=verify|฿dm=score|฿dn=impact|฿do=organization|฿dp=terms|฿dq=recognition|฿dr=path|฿ds=variable|฿dt=adaptive|฿du=graph|฿dv=awcloud|฿dw=dynamic|฿dx=tool|฿dy=navigation|฿dz=design|฿e=based|฿ea=steps|฿eb=testing|฿ec=processing|฿ed=time|฿ee=override|฿ef=immediate|฿eg=sources|฿eh=assistant|฿ei=english|฿ej=translation|฿ek=advanced|฿el=viii|฿em=functional|฿en=assurance|฿eo=methodology|฿ep=mind|฿eq=references|฿er=maintained|฿es=database|฿et=test|฿eu=file|฿ev=risk|฿ew=speed|฿ex=frameworks|฿ey=codes|฿ez=corrections|฿f=cross|฿fa=role|฿fb=duplication|฿fc=configuration|฿fd=websearch|฿fe=structure|฿ff=absolute|฿fg=philosophy|฿fh=enhancement|฿fi=development|฿fj=adaptation|฿fk=workflow|฿fl=flow|฿fm=confidence|฿fn=audit|฿fo=between|฿fp=correct|฿fq=request|฿fr=behavior|฿fs=simple|฿ft=gate|฿fu=preservation|฿fv=using|฿fw=line|฿fx=after|฿fy=rule|฿fz=architect|฿g=basis|฿ga=json|฿gb=paths|฿gc=webfetch|฿gd=config|฿ge=into|฿gf=components|฿gg=profile|฿gh=communication|฿gi=intent|฿gj=mockup|฿gk=persona|฿gl=control|฿gm=lifecycle|฿gn=tree|฿go=summary|฿gp=runtime|฿gq=levels|฿gr=tools|฿gs=guidelines|฿gt=tasks|฿gu=requiring|฿gv=ensure|฿gw=follow|฿gx=actions|฿gy=metacognition|฿gz=current|฿h=compliance|฿ha=coverage|฿hb=while|฿hc=roles|฿hd=layers|฿he=every|฿hf=text|฿hg=against|฿hh=validate|฿hi=maintain|฿hj=rules|฿hk=natural|฿hl=developer|฿hm=thinking|฿hn=hybrid|฿ho=clarity|฿hp=memory|฿hq=enhanced|฿hr=constraints|฿hs=values|฿ht=meta|฿hu=foundation|฿hv=darkwingtm|฿hw=complete|฿hx=guessing|฿hy=chunking|฿hz=spacing|฿i=agent|฿ia=challenge|฿ib=specifications|฿ic=active|฿id=phrase|฿ie=join|฿if=concepts|฿ig=checking|฿ih=identify|฿ii=reliability|฿ij=load|฿ik=responses|฿il=used|฿im=required|฿in=across|฿io=update|฿ip=specialist|฿iq=count|฿ir=single|฿is=strategy|฿it=high|฿iu=transparency|฿iv=outdated|฿iw=priority|฿ix=battle|฿iy=insights|฿iz=full|฿j=rationale|฿ja=evidence|฿jb=extraction|฿jc=diagram|฿jd=recurring|฿je=compressed|฿jf=default|฿jg=assumptions|฿jh=problem|฿ji=acceptance|฿jj=debate|฿jk=previous|฿jl=cost|฿jm=alignment|฿jn=auditor|฿jo=exploration|฿jp=network|฿jq=error|฿jr=settings|฿js=thoughts|฿jt=evolution|฿ju=names|฿jv=scan|฿jw=live|฿jx=exception|฿jy=foundational|฿jz=research"

            template_count = 19
            phrase_count = 61
            word_count = 459

        # Build header with actual or fallback dictionaries
        header = f"""---
# 🎯 **Dictionary-Compressed Context File**
**Platform: Claude Code(CLAUDE.md)**
**AI: Lossless dictionary compression. Load dictionaries below before processing content.**
**AI: Intelligent compression - AI achieves 100% comprehension through direct pattern recognition without decompression scripts.**
**AI: Comprehension - No decompression processing required.**

## 📖 **DECOMPRESSION INSTRUCTIONS**
**For AI Systems: Instant understanding via native code mapping - no processing required**

### **Step 1: Load Dictionary Tables**
**- Read all dictionary tables below into memory**
**- Template Dictionary**: T1-T{template_count} format(structural templates)
**- Phrase Dictionary**: €a-€€bi format(multi-word phrases)
**- Word Dictionary**: $A-$V and ฿a-฿฿pq formats(single words)

### **Step 2: Apply Decompression**
**- Apply dictionaries in this order**
**1. Template Dictionary(T1-T{template_count})** - Replace template codes with full structures
**2. Phrase Dictionary(€a-€€bi)** - Replace phrase codes with complete phrases
**3. Word Dictionary($A-$V, ฿a-฿฿pq)** - Replace word codes with individual words

### **Step 3: Process Normally**
**- After decompression, the content is standard CLAUDE.md format - process as normal.**

#**⚠️ CRITICAL REMINDER:**
**- Designed for AI, NOT human reading**
**- Manual decompression = errors**
**- AI auto-decodes 100% accuracy and understand**
**- Humans: plain language only**
**- No codes/abbreviations with humans**
**- Use plain language only**
**- No €ah-€ai, $D X, etc.**
**- Always explain clearly**
---

## 📚 **DICTIONARY TABLES**

### **Template Dictionary({template_count} entries)**
```
{template_table}
```

### **Phrase Dictionary ({phrase_count} entries)**
```
{phrase_table}
```

### **Word Dictionary ({word_count}+ entries)**
```
{word_table}
```

---
"""
        return header

    def _build_normal_header_2000(self, config: HeaderConfig) -> str:
        """Build 2000-word dictionary header"""
        return self._build_normal_header_1599(config).replace('1599', '2000')

    def _build_normal_header_default(self, config: HeaderConfig) -> str:
        """Build default/minimal header"""
        return """# DECOMPRESSION INSTRUCTIONS
## Standard Header (Minimal Dictionary)

AI systems: Load dictionaries and decompress normally.
"""


class ZipModeStrategy(HeaderStrategy):
    """
    Minimal header + compression metadata only.

    For ZIP-compressed content, stores only metadata and
    decompression instructions. Dictionary tables are
    compressed inside ZIP, not displayed in header.
    """

    def generate(self, config: HeaderConfig) -> str:
        """Generate minimal zip-mode header"""
        header = f"""# ZIP-COMPRESSED CONTENT

**Compression**: Level {config.compression_level}
**Dictionary**: {'Full (1599)' if config.dictionary_set == '1599' else config.dictionary_set}
**Encoding**: base64 + gzip

## Decompression Instructions:

1. Decode from base64
2. Decompress with gzip
3. Load dictionaries from decompressed content
4. Apply dictionary replacements
5. Process as normal content

## Status:
✅ Fully reversible
✅ 100% data integrity
✅ AI compatible
"""
        return header

    def validate(self, header: str) -> bool:
        """Check header has compression metadata"""
        return 'Compression:' in header or 'ZIP' in header


class CustomModeStrategy(HeaderStrategy):
    """
    User-defined header generation.

    Allows custom header content via metadata configuration.
    Useful for specialized deployment scenarios.
    """

    def generate(self, config: HeaderConfig) -> str:
        """Generate custom header from metadata"""
        if config.metadata and 'custom_content' in config.metadata:
            return config.metadata['custom_content']

        # Fallback to minimal header
        return """# CUSTOM HEADER

Custom header mode enabled.
Provide 'custom_content' in metadata for header generation.
"""

    def validate(self, header: str) -> bool:
        """Custom mode accepts any non-empty header"""
        return len(header) > 0


class StrategyRegistry:
    """
    Registry of available header strategies.

    Provides discovery and lookup of registered strategies.
    """

    _builtin_strategies = {
        'normal': NormalModeStrategy,
        'zip': ZipModeStrategy,
        'custom': CustomModeStrategy,
    }

    @classmethod
    def get_builtin_strategies(cls) -> Dict[str, type]:
        """Get all built-in strategies"""
        return cls._builtin_strategies.copy()

    @classmethod
    def describe_strategy(cls, name: str) -> Dict[str, Any]:
        """Get strategy description"""
        if name not in cls._builtin_strategies:
            return {}

        strategy_class = cls._builtin_strategies[name]
        instance = strategy_class()
        return {
            'name': name,
            'class': strategy_class.__name__,
            'docstring': strategy_class.__doc__,
            'metadata': instance.get_metadata(),
        }

    @classmethod
    def list_strategies(cls) -> list:
        """List all available strategy names"""
        return list(cls._builtin_strategies.keys())
