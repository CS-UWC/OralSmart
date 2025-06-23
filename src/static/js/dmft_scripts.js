// DMFT Assessment JavaScript
// File: static/js/dmft_scripts.js

// DMFT Calculation Functions
function updateDMFTSummary() {
    let decayed = 0, missing = 0, filled = 0;
    
    // Count permanent teeth
    const permanentSelects = document.querySelectorAll('.permanent-tooth');
    permanentSelects.forEach(select => {
        const value = select.value;
        if (value === '1') decayed++;
        else if (value === '2') filled++;
        else if (value === '3' || value === '4') missing++;
    });
    
    // Count primary teeth
    const primarySelects = document.querySelectorAll('.primary-tooth');
    primarySelects.forEach(select => {
        const value = select.value;
        if (value === 'B') decayed++;
        else if (value === 'C') filled++;
        else if (value === 'D' || value === 'E') missing++;
    });
    
    // Update display
    const decayedElement = document.getElementById('decayed-count');
    const missingElement = document.getElementById('missing-count');
    const filledElement = document.getElementById('filled-count');
    const totalElement = document.getElementById('total-dmft');
    
    if (decayedElement) decayedElement.textContent = decayed;
    if (missingElement) missingElement.textContent = missing;
    if (filledElement) filledElement.textContent = filled;
    if (totalElement) totalElement.textContent = decayed + missing + filled;
}

// Checkbox management for dietary section
function setupCheckboxGroups() {
    // Sweet foods yes/no
    const sweetYes = document.getElementById('sweet_yes');
    const sweetNo = document.getElementById('sweet_no');
    
    if (sweetYes && sweetNo) {
        sweetYes.addEventListener('change', function() {
            if (this.checked) sweetNo.checked = false;
        });
        
        sweetNo.addEventListener('change', function() {
            if (this.checked) sweetYes.checked = false;
        });
    }
    
    // Daily frequency (only one selection)
    const dailyCheckboxes = document.querySelectorAll('input[name="daily_frequency"]');
    dailyCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                dailyCheckboxes.forEach(other => {
                    if (other !== this) other.checked = false;
                });
            }
        });
    });
    
    // Weekly frequency (only one selection)
    const weeklyCheckboxes = document.querySelectorAll('input[name="weekly_frequency"]');
    weeklyCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                weeklyCheckboxes.forEach(other => {
                    if (other !== this) other.checked = false;
                });
            }
        });
    });
}

// Reset form function
function resetForm() {
    if (confirm('Are you sure you want to reset the form? All data will be lost.')) {
        const form = document.querySelector('form');
        if (form) {
            form.reset();
            updateDMFTSummary();
        }
    }
}

// Auto-calculate age based on date of birth
function setupAgeCalculation() {
    const dobInput = document.getElementById('date_of_birth');
    const ageInput = document.getElementById('age');
    
    if (dobInput && ageInput) {
        dobInput.addEventListener('change', function() {
            const dob = new Date(this.value);
            const today = new Date();
            const age = Math.floor((today - dob) / (365.25 * 24 * 60 * 60 * 1000));
            
            if (age > 0 && age <= 18) {
                ageInput.value = age;
            }
        });
    }
}

// Function to get DMFT data for form submission
function getDMFTData() {
    const decayedElement = document.getElementById('decayed-count');
    const missingElement = document.getElementById('missing-count');
    const filledElement = document.getElementById('filled-count');
    const totalElement = document.getElementById('total-dmft');
    
    return {
        decayed: decayedElement ? parseInt(decayedElement.textContent) : 0,
        missing: missingElement ? parseInt(missingElement.textContent) : 0,
        filled: filledElement ? parseInt(filledElement.textContent) : 0,
        total: totalElement ? parseInt(totalElement.textContent) : 0
    };
}

// Function to reset DMFT calculations
function resetDMFT() {
    const selects = document.querySelectorAll('.tooth-select');
    selects.forEach(select => {
        select.value = '';
    });
    updateDMFTSummary();
}

// Form validation
function validateForm() {
    // Add your validation logic here
    let isValid = true;
    const requiredFields = document.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DMFT Assessment loaded');
    
    // Add event listeners to all tooth select elements
    const toothSelects = document.querySelectorAll('.tooth-select');
    toothSelects.forEach(select => {
        select.addEventListener('change', updateDMFTSummary);
    });
    
    // Setup checkbox groups
    setupCheckboxGroups();
    
    // Setup age calculation
    setupAgeCalculation();
    
    // Initial calculation
    updateDMFTSummary();
    
    // Add form submission handler
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }
});

// Export functions for external use
window.DMFTAssessment = {
    updateSummary: updateDMFTSummary,
    resetForm: resetForm,
    getDMFTData: getDMFTData,
    resetDMFT: resetDMFT,
    validateForm: validateForm
};