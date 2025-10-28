import TimetableHeader from "@/components/timetable-header";
import { Calendar } from "@/components/calendar";
import Head from "next/head";
import { useState } from "react";

export default function Home() {
  // State to hold the selected timetable ID
  // This will be passed to the Calendar component to fetch and display the correct timetable
  const [selectedTimetable, setSelectedTimetable] = useState<number | null>(
    null
  );

  return (
    <>
      <Head>
        <title>Stundenplan</title>
      </Head>
      <TimetableHeader
        selectedTimetable={selectedTimetable}
        onSelectTimetable={setSelectedTimetable}
      />
      <main>
        <Calendar selectedTimetable={selectedTimetable} />
      </main>
    </>
  );
}
