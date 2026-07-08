package capstone.capstone2026.dto;

import java.util.HashMap;
import java.util.Map;

public class AnalysisResult {
    private String diseaseName;
    private double finalScore;
    private String finalStatus; 
    private Map<String, String> nutrientStatuses = new HashMap<>();
    // 대시보드 권장량 계산을 위해 각 영양소의 한 끼 임계치(Threshold) 저장용 맵 추가
    private Map<String, Double> nutrientThresholds = new HashMap<>();

    public AnalysisResult(String diseaseName) {
        this.diseaseName = diseaseName;
    }

    public void addNutrient(String name, int score) {
        String status = (score == 100) ? "안전" : (score == 50 ? "주의" : "위험");
        nutrientStatuses.put(name, status);
    }

    // 서비스 레이어에서 임계치를 기록할 수 있도록 메서드 추가
    public void addNutrientWithThreshold(String name, int score, double threshold) {
        addNutrient(name, score);
        nutrientThresholds.put(name, threshold);
    }

    public void calculateFinal(double score) {
        this.finalScore = score;
        if (score >= 80) this.finalStatus = "안전";
        else if (score >= 50) this.finalStatus = "주의";
        else this.finalStatus = "위험";
    }

    public String getDiseaseName() { return diseaseName; }
    public double getFinalScore() { return finalScore; }
    public String getFinalStatus() { return finalStatus; }
    public Map<String, String> getNutrientStatuses() { return nutrientStatuses; }
    // 서비스에서 꺼내 쓸 수 있도록 Getter 추가
    public Map<String, Double> getNutrientThresholds() { return nutrientThresholds; }
}