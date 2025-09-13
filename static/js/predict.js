// Prediction form functionality
document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    const predictionResult = document.getElementById('predictionResult');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitButton = predictionForm.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Predicting...';
            submitButton.disabled = true;
            
            try {
                // Collect form data
                const formData = {
                    temperature: parseFloat(document.getElementById('temperature').value),
                    humidity: parseFloat(document.getElementById('humidity').value),
                    air_quality: parseFloat(document.getElementById('air_quality').value),
                    wind_speed: parseFloat(document.getElementById('wind_speed').value),
                    precipitation: parseFloat(document.getElementById('precipitation').value),
                    population_density: parseFloat(document.getElementById('population_density').value),
                    building_density: parseFloat(document.getElementById('building_density').value),
                    hour_of_day: parseInt(document.getElementById('hour_of_day').value),
                    day_of_week: parseInt(document.getElementById('day_of_week').value),
                    is_holiday: document.getElementById('is_holiday').value === 'true'
                };
                
                // Add optional fields if they have values
                const latitude = document.getElementById('latitude').value;
                const longitude = document.getElementById('longitude').value;
                const locationName = document.getElementById('location_name').value;
                
                if (latitude) formData.latitude = parseFloat(latitude);
                if (longitude) formData.longitude = parseFloat(longitude);
                if (locationName) formData.location_name = locationName;
                
                // Make prediction request
                const response = await makeRequest('/api/predict/', 'POST', formData);
                
                // Display results
                displayPredictionResult(response);
                
            } catch (error) {
                console.error('Prediction error:', error);
                showNotification('Error making prediction. Please try again.', 'danger');
            } finally {
                // Restore button state
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
            }
        });
    }
    
    function displayPredictionResult(result) {
        const severityClass = `emergency-${result.severity}`;
        const emergencyIcon = getEmergencyIcon(result.emergency_type);
        const severityColor = getSeverityColor(result.severity);
        
        // Create probability bars HTML
        let probabilityBars = '';
        for (const [emergencyType, probability] of Object.entries(result.probabilities)) {
            const percentage = (probability * 100).toFixed(2);
            const barColor = getBarColorForEmergency(emergencyType);
            
            probabilityBars += `
                <div class="mb-2">
                    <div class="d-flex justify-content-between">
                        <span class="text-capitalize">${emergencyType.replace('_', ' ')}</span>
                        <span>${percentage}%</span>
                    </div>
                    <div class="probability-bar">
                        <div class="probability-fill" style="width: ${percentage}%; background-color: ${barColor};">
                            ${percentage}%
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Create recommendations HTML
        let recommendationsHtml = '';
        if (result.recommendations && result.recommendations.length > 0) {
            recommendationsHtml = `
                <div class="mt-4">
                    <h5><i class="fas fa-lightbulb me-2"></i>Recommendations</h5>
                    <ul class="list-group">
                        ${result.recommendations.map(rec => `<li class="list-group-item">${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Create result HTML
        const resultHtml = `
            <div class="card shadow ${severityClass}">
                <div class="card-header bg-${severityColor} text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas ${emergencyIcon} me-2"></i>
                        Prediction Result
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="alert alert-${severityColor}">
                                <h4 class="alert-heading text-capitalize">
                                    ${result.emergency_type.replace('_', ' ')} Emergency
                                </h4>
                                <p class="mb-0">
                                    <strong>Severity:</strong> 
                                    <span class="text-capitalize">${result.severity}</span>
                                </p>
                                <p class="mb-0">
                                    <strong>Confidence:</strong> 
                                    ${(result.confidence * 100).toFixed(2)}%
                                </p>
                                <p class="mb-0">
                                    <strong>Time:</strong> 
                                    ${formatDate(result.timestamp)}
                                </p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h5>Probability Distribution</h5>
                            ${probabilityBars}
                        </div>
                    </div>
                    ${recommendationsHtml}
                    <div class="mt-3 text-center">
                        <button class="btn btn-outline-primary me-2" onclick="window.location.reload()">
                            <i class="fas fa-redo me-2"></i>Make Another Prediction
                        </button>
                        <button class="btn btn-outline-secondary" onclick="window.location.href='{% url 'dashboard' %}'">
                            <i class="fas fa-chart-line me-2"></i>View Dashboard
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Display result
        predictionResult.innerHTML = resultHtml;
        predictionResult.style.display = 'block';
        
        // Scroll to result
        predictionResult.scrollIntoView({ behavior: 'smooth' });
    }
    
    function getBarColorForEmergency(emergencyType) {
        const colors = {
            'fire': '#dc3545',
            'accident': '#fd7e14',
            'medical': '#ffc107',
            'natural_disaster': '#6f42c1',
            'none': '#28a745'
        };
        return colors[emergencyType] || '#6c757d';
    }
});