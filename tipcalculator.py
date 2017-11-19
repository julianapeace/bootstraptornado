def exercise8():
    bill = float(input("Total bill amount?"))
    service = input("Level of service? Write 'good','fair', or 'bad'")
    service = service.lower()
    if service == "good":
        tip = bill * 0.20
    elif service == "fair":
        tip = bill * 0.15
    else:
        tip = bill * 0.10
    people = int(input("Split how many ways? Enter integer."))
    totalbill = bill + tip
    split = totalbill / people
    print("Service was", service, "\n", "Tip amount:", "\t", tip, "\n",
          "Total amount:", "\t", totalbill, "\n", "Amount per person:", "\t", split)
