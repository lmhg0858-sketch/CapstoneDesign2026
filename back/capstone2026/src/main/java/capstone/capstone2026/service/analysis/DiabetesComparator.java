package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.AnalysisResult;
import org.springframework.stereotype.Component;

@Component
public class DiabetesComparator implements DiseaseComparator {
    @Override public String getDiseaseName() { return "당뇨"; }

    @Override
    public AnalysisResult evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        AnalysisResult res = new AnalysisResult(getDiseaseName());
        if (n.getKcal() <= 0) { res.calculateFinal(100); return res; }

        double h = user.getHeight() / 100.0;
        double sw = ("MALE".equalsIgnoreCase(user.getGender()) || "남성".equals(user.getGender())) ? Math.pow(h, 2) * 22 : Math.pow(h, 2) * 21;
        double limit = (sw * 30.0) / 3.0;

        double cPct = (n.getCarbs() * 4 / n.getKcal()) * 100;
        double fPct = (n.getFat() * 9 / n.getKcal()) * 100;

        int cS = (cPct < 50 || cPct > 70) ? 0 : (cPct < 55 || cPct > 65 ? 50 : 100);
        int fS = (fPct < 10 || fPct > 45) ? 0 : (fPct < 20 || fPct > 35 ? 50 : 100);
        int sS = (n.getSugar() >= 20) ? 0 : (n.getSugar() >= 16 ? 50 : 100);
        int kS = (n.getKcal() > limit + 100) ? 0 : (n.getKcal() > limit ? 50 : 100);

        res.addNutrient("탄수화물", cS);
        res.addNutrient("지방", fS);
        res.addNutrient("당", sS);
        res.addNutrient("칼로리", kS);
        res.calculateFinal(cS * 0.3 + fS * 0.2 + sS * 0.3 + kS * 0.2);
        return res;
    }
}