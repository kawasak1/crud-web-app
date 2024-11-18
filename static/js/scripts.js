const tableSchemas = {
  users: [
    { id: "email", label: "Email", type: "email", required: true },
    { id: "name", label: "Name", type: "text", required: false },
    { id: "surname", label: "Surname", type: "text", required: false },
    { id: "salary", label: "Salary", type: "number", required: false },
    { id: "phone", label: "Phone", type: "text", required: false },
    { id: "cname", label: "Country", type: "text", required: false },
  ],
  patients: [
    { id: "email", label: "Email", type: "email", required: true },
    { id: "name", label: "Name", type: "text", required: false, edit: true },
    { id: "surname", label: "Surname", type: "text", required: false, edit: true },
    { id: "disease_code", label: "Disease Code", type: "text", required: false },
  ],
  doctors: [
    { id: "email", label: "Email", type: "email", required: true },
    { id: "name", label: "Name", type: "text", required: false, edit: true },
    { id: "surname", label: "Surname", type: "text", required: false, edit: true },
    { id: "degree", label: "Degree", type: "text", required: false },
    { id: "department", label: "Department", type: "text", required: false },
  ],
  specializations: [
    { id: "email", label: "Email", type: "email", required: true, add: true },
    { id: "specialization_id", label: "Disease ID", type: "number", required: true },
  ],
  diseases: [
    { id: "disease_code", label: "Disease Code", type: "text", required: true},
    { id: "pathogen", label: "Pathogen", type: "text"},
    { id: "disease_description", label: "Disease Description", type: "text"},
    { id: "disease_type_id", label: "Disease Type ID", type: "number"},
    { id: "first_encounter_date", label: "First Encounter Date", type: "text"},
    { id: "country_of_discover", label: "Country of Discover", type: "text"},
  ],
  countries: [
    { id: "country_name", label: "Country Name", type: "text", required: true},
    { id: "population", label: "Population", type: "number"},
  ],
  records: [
    { id: "email", label: "Email", type: "email", required: true},
    { id: "cname", label: "Country Name", type: "text", required: true},
    { id: "disease_code", label: "Disease Code", type: "text", required: true},
    { id: "total_deaths", label: "Total Deaths", type: "number", required: false },
    { id: "total_patients", label: "Total Patients", type: "number", required: false },
  ],
};
let currentAction = "";
let currentTable = "";
let currentData = "";

function openModal(action, table, data = {}) {
  const modal = document.getElementById("dataModal");
  const modalTitle = document.getElementById("modalTitle");
  const form = document.getElementById("dynamicForm");

  currentAction = action;
  currentTable = table;
  currentData = data;

  // Set modal title based on action
  modalTitle.textContent = action === "edit" ? `Edit ${table}` : `Add ${table}`;

  // Clear existing fields
  form.innerHTML = "";

  // Generate fields dynamically based on the schema
  const schema = tableSchemas[table] || [];
  schema.forEach((field) => {
    if ((action == "edit" && !field.add) || (action == "add" && !field.edit)) {
      const value = data[field.id] || "";
      const fieldElement = document.createElement("div");
      fieldElement.className = "mb-3";

      const label = document.createElement("label");
      label.setAttribute("for", field.id);
      label.textContent = field.label;

      const input = document.createElement("input");
      input.id = field.id;
      input.name = field.id;
      input.type = field.type;
      input.value = value;
      input.required = field.required;
      input.className = "form-control";
      input.disabled = field.disabled;

      fieldElement.appendChild(label);
      fieldElement.appendChild(input);
    form.appendChild(fieldElement);
    }
  });

  modal.style.display = "block"; // Show modal
}

function closeModal() {
  document.getElementById("dataModal").style.display = "none";
}

function submitForm(table) {
  const form = document.getElementById("dynamicForm");
  const formData = new FormData(form);
  const data = {};

  // Convert form data to a JSON object
  formData.forEach((value, key) => {
      data[key] = value;
  });

  data["old"] = currentData;

  // Send the updated data to the server via AJAX
  const xhr = new XMLHttpRequest();
  xhr.open("POST", currentAction == "edit" ? `/update/${table}` : `/add/${table}`, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify(data));

  xhr.onload = function () {
      if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          alert(response.message);
          window.location.reload();
      } else {
          const response = JSON.parse(xhr.responseText);
          alert(response.error);
          console.log("Error updating data:", xhr.responseText);
      }
  };
}

function deleteData(table, data) {
  // Confirm deletion action
  if (confirm("Are you sure you want to delete this row?")) {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `/delete/${table}`, true);
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.send(JSON.stringify(data));

      xhr.onload = function () {
          if (xhr.status === 200) {
              const response = JSON.parse(xhr.responseText);
              alert(response.message);
              window.location.reload();
          } else {
              const response = JSON.parse(xhr.responseText);
              alert(response.error);
              console.log("Error updating data:", xhr.responseText);
          }
      };
  }
}