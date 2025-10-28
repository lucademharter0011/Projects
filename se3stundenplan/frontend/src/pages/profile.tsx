import Heading from "@/components/heading";
import { Timetable, User } from "@/types";
import { Calendar, Globe, Mail, Shield, UserIcon } from "lucide-react";
import { useSession } from "next-auth/react";
import Head from "next/head";
import { useEffect, useState } from "react";

export default function Profile() {
  const { data: session } = useSession();
  const [profile, setProfile] = useState<User | null>(null);
  const [timetables, setTimetables] = useState<Timetable[]>([]);

  useEffect(() => {
    if (!session) return;

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session!.user.accessToken}`,
      },
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.statusText);
        return response.json();
      })
      .then((data) => setProfile(data.user))
      .catch((error) => console.error("Failed to load profile:", error));

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/timetable/`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session!.user.accessToken}`,
      },
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.statusText);
        return response.json();
      })
      .then((data) => setTimetables(data.timetables || []))
      .catch((error) => console.error("Failed to load timetables:", error));
  }, [session]);

  return (
    <>
      <Head>
        <title>{profile?.full_name} | Stundenplan</title>
      </Head>
      <main className="py-15">
        <Heading
          title="Profil"
          description="Alle Informationen über dein Profil."
        />
        <div className="max-w-3xl py-4">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                    {profile?.full_name?.charAt(0) ||
                      profile?.email?.charAt(0) ||
                      "U"}
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-green-500 rounded-full border-4 border-white flex items-center justify-center">
                    <div className="w-3 h-3 bg-white rounded-full"></div>
                  </div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {profile?.full_name || "Unbekannter Nutzer"}
                  </h1>
                  <p className="text-gray-600 text-lg">
                    @{profile?.username || "username"}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Mitglied seit{" "}
                    {profile?.created_at
                      ? new Date(profile.created_at).toLocaleDateString("de-DE")
                      : "Unbekannt"}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <UserIcon className="w-5 h-5 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Persönliche Daten
                </h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Mail className="w-5 h-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">E-Mail</p>
                    <p className="font-medium text-gray-900">
                      {profile?.email || "Nicht angegeben"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <UserIcon className="w-5 h-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Benutzername</p>
                    <p className="font-medium text-gray-900">
                      {profile?.username || "Nicht angegeben"}
                    </p>
                  </div>
                </div>

                {profile?.student_id && (
                  <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <Calendar className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Matrikelnummer</p>
                      <p className="font-medium text-gray-900">
                        {profile.student_id}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <Shield className="w-5 h-5 text-green-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Konto-Einstellungen
                </h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Zeitzone</p>
                    <p className="text-sm text-gray-500">
                      {profile?.timezone || "Nicht festgelegt"}
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    {profile?.timezone || "Standard"}
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">
                      Benachrichtigungen
                    </p>
                    <p className="text-sm text-gray-500">
                      Erhalte Updates und Erinnerungen
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 text-sm font-medium rounded-full ${
                      profile?.notifications_enabled
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {profile?.notifications_enabled
                      ? "Aktiviert"
                      : "Deaktiviert"}
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">
                      Design-Präferenz
                    </p>
                    <p className="text-sm text-gray-500">
                      Dein bevorzugtes Theme
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-medium rounded-full">
                    {profile?.theme_preference === "dark"
                      ? "Dunkel"
                      : profile?.theme_preference === "light"
                      ? "Hell"
                      : profile?.theme_preference === "system"
                      ? "System"
                      : "Standard"}
                  </span>
                </div>
              </div>
            </div>
          </div>
          {timetables && timetables.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mt-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-indigo-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Stundenplan
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {timetables.map((timetable, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100"
                  >
                    <h3 className="font-semibold text-gray-900 mb-2">
                      {timetable.name || `Stundenplan ${index + 1}`}
                    </h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      {timetable.semester && (
                        <p>Semester: {timetable.semester}</p>
                      )}
                      {timetable.courses && (
                        <p>Kurse: {timetable.courses.length}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mt-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <Globe className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Aktivität</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <p className="text-2xl font-bold text-gray-900">
                  {profile?.created_at
                    ? new Date(profile.created_at).toLocaleDateString("de-DE")
                    : "Unbekannt"}
                </p>
                <p className="text-sm text-gray-500">Beigetreten am</p>
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <p className="text-2xl font-bold text-gray-900">
                  {timetables?.length || 0}
                </p>
                <p className="text-sm text-gray-500">Stundenpläne</p>
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <p className="text-2xl font-bold text-gray-900">
                  {profile?.created_at
                    ? Math.floor(
                        (Date.now() - new Date(profile.created_at).getTime()) /
                          (1000 * 60 * 60 * 24)
                      )
                    : 0}
                </p>
                <p className="text-sm text-gray-500">Tage Mitglied</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
