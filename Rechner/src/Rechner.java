
import java.util.ArrayList;
import java.util.Scanner;
import static java.lang.Integer.parseInt;
public class Rechner {
    int Ergebnis;
    public static String Rechnen(String Zahl1,String Zahl2, String Rechenzeichen ){
        int UmZahl1=parseInt(Zahl1);
        int UmZahl2=parseInt(Zahl2);
        String Ergebnis;
        switch(Rechenzeichen){
            case "+":return Integer.toString(Integer.sum(UmZahl1, UmZahl2));
            case "-":return Integer.toString(UmZahl1-UmZahl2);
            case "*":return Integer.toString(UmZahl1*UmZahl2);
            case "/":return Integer.toString(UmZahl1/UmZahl2);
            default: return null;
        }
    }

    public static boolean istRechenzeichen(String Zeichen) {
        switch (Zeichen) {
            case "+", "/", "-", "*":
                return true;
            default:
                return false;
        }
    }

    public static boolean istZahl(String Zeichen) {
        try {
            int Zahl = parseInt(Zeichen);
        } catch (NumberFormatException e) {
            return false;
        }
        return true;
    }

    public static void main(String[] args) {
        int Ergebnis = 0;
        Scanner scanner = new Scanner(System.in);
        System.out.println("Gib deine Werte ein");
        String Eingabe = scanner.nextLine();
        if (Eingabe == "Ende") {
            System.exit(1);
        }
        String[] Eingabegesplittet = Eingabe.split(" ");
        ArrayList<String> Eingabefinal=new ArrayList<>();
        for (int i = 0;i<Eingabegesplittet.length; i++) {
            if (Eingabegesplittet[i].equals("e")) {
                Eingabegesplittet[i]="3.14";
            }
            if (!istZahl(Eingabegesplittet[i])&&!istRechenzeichen(Eingabegesplittet[i])){
                System.out.println("Fehler bei Eingabe");
            }
            Eingabefinal.add(i,Eingabegesplittet[i]);
            }
        while (Eingabefinal.size()> 1) {
            for(int i=0; i<Eingabefinal.size();i++){
                if(istRechenzeichen(Eingabefinal.get(i))){
                    Eingabefinal.set(i,Rechnen(Eingabefinal.get(i-2), Eingabefinal.get(i-1), Eingabefinal.get(i)));
                    Eingabefinal.remove(Eingabefinal.get(i-2));
                    Eingabefinal.remove(Eingabefinal.get(i-2));
                    break;
                }

            }
        }
        Ergebnis=parseInt(Eingabefinal.getFirst());
        System.out.println(Ergebnis);
    }
}