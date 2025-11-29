import pandas as pd
from .config import SAMPLE_QUERIES_PATH
from .nlp_module import interpretar_consulta
from .features import jaccard, split_comma


def parse_skills_semicolon(skills_str: str):
    if not isinstance(skills_str, str):
        return []
    return [s.strip().lower() for s in skills_str.split(";") if s.strip()]


def normalizar_simple(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower().replace('"', "")
    return s


def main():
    df = pd.read_csv(SAMPLE_QUERIES_PATH)

    total = len(df)
    aciertos_cargo = 0
    aciertos_ubicacion = 0
    aciertos_experiencia = 0

    jaccards_skills = []

    for _, row in df.iterrows():
        texto = row["query_text"]
        gt_role = normalizar_simple(row.get("role", ""))
        gt_location = normalizar_simple(row.get("location", ""))
        gt_exp = int(row.get("experience_years", 0) or 0)
        gt_skills = parse_skills_semicolon(row.get("skills", ""))

        pred = interpretar_consulta(texto)
        pred_cargo = normalizar_simple(pred.get("cargo", ""))
        pred_ubicacion = normalizar_simple(pred.get("ubicacion", ""))
        pred_exp = int(pred.get("experiencia_minima", 0) or 0)
        pred_skills = [s.lower() for s in pred.get("habilidades", [])]

        if gt_role and gt_role in pred_cargo:
            aciertos_cargo += 1

        if gt_location and gt_location in pred_ubicacion:
            aciertos_ubicacion += 1

        if gt_exp == pred_exp:
            aciertos_experiencia += 1

        j = jaccard(gt_skills, pred_skills)
        jaccards_skills.append(j)

        print("--------------------------------------------------")
        print("Consulta:", texto)
        print("GT role:", gt_role, "| Pred cargo:", pred_cargo)
        print("GT loc :", gt_location, "| Pred ubicacion:", pred_ubicacion)
        print("GT exp :", gt_exp, "| Pred exp:", pred_exp)
        print("GT skills:", gt_skills, "| Pred skills:", pred_skills)
        print("Jaccard skills:", round(j, 3))

    print("\n================== RESUMEN ==================")
    print(f"Consultas evaluadas: {total}")
    print(f"Accuracy cargo      : {aciertos_cargo}/{total} = {aciertos_cargo/total:.2f}")
    print(f"Accuracy ubicación  : {aciertos_ubicacion}/{total} = {aciertos_ubicacion/total:.2f}")
    print(f"Accuracy experiencia: {aciertos_experiencia}/{total} = {aciertos_experiencia/total:.2f}")
    if jaccards_skills:
        print(f"Jaccard medio skills: {sum(jaccards_skills)/len(jaccards_skills):.2f}")


if __name__ == "__main__":
    main()
