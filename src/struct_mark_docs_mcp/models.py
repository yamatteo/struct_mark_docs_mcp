from pydantic import BaseModel, Field


class SubsubsectionMeta(BaseModel):
    title: str
    abstract: str = ""
    wc: int = 0


class SubsectionMeta(BaseModel):
    title: str
    abstract: str = ""
    wc: int = 0
    subsubsections: list[SubsubsectionMeta] = Field(default_factory=list)


class SectionMeta(BaseModel):
    title: str
    abstract: str = ""
    wc: int = 0
    subsections: list[SubsectionMeta] = Field(default_factory=list)


class FileFrontmatter(BaseModel):
    title: str
    abstract: str = ""
    wc: int = 0
    toc: list[SectionMeta] = Field(default_factory=list)
    refs: list[str] = Field(default_factory=list)
    back_refs: list[str] = Field(default_factory=list)

    def to_ordered_dict(self) -> dict:
        """Serialize to an ordered dict with canonical key order for YAML output."""
        result: dict = {
            "title": self.title,
            "abstract": self.abstract,
            "wc": self.wc,
            "toc": [],
            "refs": self.refs,
            "back_refs": self.back_refs,
        }
        for sec in self.toc:
            sec_dict: dict = {
                "title": sec.title,
                "abstract": sec.abstract,
                "wc": sec.wc,
                "subsections": [],
            }
            for sub in sec.subsections:
                sub_dict: dict = {
                    "title": sub.title,
                    "abstract": sub.abstract,
                    "wc": sub.wc,
                    "subsubsections": [],
                }
                for subsub in sub.subsubsections:
                    sub_dict["subsubsections"].append({
                        "title": subsub.title,
                        "abstract": subsub.abstract,
                        "wc": subsub.wc,
                    })
                if not sub_dict["subsubsections"]:
                    del sub_dict["subsubsections"]
                sec_dict["subsections"].append(sub_dict)
            if not sec_dict["subsections"]:
                del sec_dict["subsections"]
            result["toc"].append(sec_dict)
        return result
