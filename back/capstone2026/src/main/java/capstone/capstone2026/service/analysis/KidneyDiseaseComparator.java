package capstone.capstone2026.service.analysis;

import capstone.capstone2026.domain.User;
import capstone.capstone2026.dto.FoodAnalysisRequest;
import capstone.capstone2026.dto.AnalysisResult;
import org.springframework.stereotype.Component;

@Component
public class KidneyDiseaseComparator implements DiseaseComparator {
    @Override public String getDiseaseName() { return "신장질환"; }

    @Override
    public AnalysisResult evaluate(FoodAnalysisRequest.NutrientData n, User user) {
        AnalysisResult res = new AnalysisResult(getDiseaseName());
        double protLimit = user.getWeight() * 1.2;

        int sodS = (n.getSodium() / 20.0 > 40) ? 0 : (n.getSodium() / 20.0 > 25 ? 50 : 100);
        int kalS = (n.getKalium() / 20.0 > 40) ? 0 : (n.getKalium() / 20.0 > 25 ? 50 : 100);
        int phoS = (n.getPhos() / 8.0 > 40) ? 0 : (n.getPhos() / 8.0 > 25 ? 50 : 100);
        double pPct = n.getProtein() / protLimit * 100;
        int protS = (pPct < 15 || pPct > 50) ? 0 : (pPct < 25 || pPct > 40 ? 50 : 100);

        res.addNutrient("나트륨", sodS);
        res.addNutrient("칼륨", kalS);
        res.addNutrient("인", phoS);
        res.addNutrient("단백질", protS);
        res.calculateFinal(sodS * 0.3 + kalS * 0.25 + phoS * 0.25 + protS * 0.2);
        return res;
    }
}