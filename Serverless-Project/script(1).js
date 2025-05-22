
document.getElementById("resumeJobForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Stop default form submission

    const apiUrl = "https://4opd51rozj.execute-api.ap-south-1.amazonaws.com/implement/resume"; // Replace with your actual API Gateway URL

    // Collect form data
    const formData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        address: document.getElementById("address").value,
        college: document.getElementById("college").value,
        degree: document.getElementById("degree").value,
        year: document.getElementById("year").value,
        skills: document.getElementById("skills").value,
        jobRole: document.getElementById("jobRole").value,
        jobLocation: document.getElementById("jobLocation").value,
        jobLinks: document.getElementById("jobLinks").value,
        experience: []
    };

    // Collect work experience entries
    document.querySelectorAll(".experienceEntry").forEach(exp => {
        const company = exp.querySelector(".company").value;
        const role = exp.querySelector(".role").value;
        const duration = exp.querySelector(".duration").value;

        if (company && role && duration) {
            formData.experience.push({ company, role, duration });
        }
    });

    try {
        // Send data to API Gateway
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            // Redirect to success page after submission
            window.location.href = "success.html";
        } else {
            alert("Submission failed. Please try again.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Submission failed. Please try again.");
    }
});
