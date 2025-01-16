from flask import Flask, render_template, request, redirect, url_for, jsonify
from fhir_generator import FHIRDocumentGenerator

app = Flask(__name__)

user_data = {}
medical_data = {}


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        # Administrative Data
        user_data["name"] = request.form["name"]
        user_data["surname"] = request.form["surname"]
        user_data["birth_date"] = request.form["birth_date"]
        user_data["ssn"] = request.form["ssn"]
        user_data["address"] = request.form["address"]
        user_data["native_language"] = request.form["native_language"]
        user_data["phone_number"] = request.form["phone_number"]
        user_data["email"] = request.form["email"]
        user_data["gender"] = request.form["gender"]

        # Emergency Contacts
        emergency_contact_names = request.form.getlist("emergency_contact_name[]")
        emergency_contact_phones = request.form.getlist("emergency_contact_phone[]")
        user_data["emergency_contacts"] = [
            {"name": name, "phone": phone}
            for name, phone in zip(emergency_contact_names, emergency_contact_phones)
        ]

        return redirect(url_for("medical_info"))
    return render_template("new_user.html")


@app.route("/medical_info", methods=["GET", "POST"])
def medical_info():
    if request.method == "POST":
        # Medical Information
        medical_data["height"] = request.form["height"]
        medical_data["weight"] = request.form["weight"]
        medical_data["blood_type"] = request.form["blood_type"]
        medical_data["allergies"] = request.form.getlist("allergies[]") if request.form.get(
            "allergies_question") == "Yes" else []
        medical_data["chronic_diseases"] = request.form.getlist("chronic_diseases[]") if request.form.get(
            "chronic_question") == "Yes" else []
        medical_data["pregnancy"] = request.form.get("pregnancy") if user_data.get("gender") != "Male" else None
        medical_data["medications"] = request.form.getlist("medications[]") if request.form.get(
            "medications_question") == "Yes" else []
        medical_data["care_level"] = request.form["care_level"]
        medical_data["dnr"] = request.form["dnr"]

        return redirect(url_for("registration_complete"))
    return render_template("medical_info.html", gender=user_data.get("gender", ""))


@app.route("/registration_complete", methods=["GET", "POST"])
def registration_complete():
    if request.method == "POST":
        fhir_generator = FHIRDocumentGenerator(
            name=f"{user_data['name']} {user_data.get('surname', '')}",
            birth_date=user_data["birth_date"],
            gender=user_data["gender"],
            ssn=user_data["ssn"],
            address=user_data["address"],
            email=user_data["email"],
            phone_number=user_data["phone_number"],
            allergies=medical_data.get("allergies", []),
            chronic_diseases=medical_data.get("chronic_diseases", []),
            care_level=medical_data.get("care_level"),
            dnr=medical_data.get("dnr")
        )
        fhir_document = fhir_generator.generate_fhir_document()

        return jsonify(fhir_document)

    return render_template("register.html", email=user_data.get("email", ""))

@app.route("/generate_fhir_document", methods=["GET"])
def generate_fhir_document():
    fhir_generator = FHIRDocumentGenerator(
        name=f"{user_data['name']} {user_data.get('surname', '')}",
        birth_date=user_data["birth_date"],
        gender=user_data["gender"],
        ssn=user_data["ssn"],
        address=user_data["address"],
        email=user_data["email"],
        phone_number=user_data["phone_number"],
        allergies=medical_data.get("allergies", []),
        chronic_diseases=medical_data.get("chronic_diseases", []),
        pregnancy=medical_data.get("pregnancy"),
        medications=medical_data.get("medications", []),
        care_level=medical_data.get("care_level"),
        dnr=medical_data.get("dnr"),
        emergency_contacts=user_data.get("emergency_contacts", [])
    )
    fhir_document = fhir_generator.generate_fhir_document()

    return jsonify(fhir_document)




if __name__ == "__main__":
    app.run(debug=True)
