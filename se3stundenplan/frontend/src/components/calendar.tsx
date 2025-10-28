import type {
  EventClickArg,
  EventContentArg,
  EventInput,
} from "@fullcalendar/core";
import FullCalendar from "@fullcalendar/react";
import { useEffect, useMemo, useState } from "react";
import { BookOpen, CalendarIcon, Clock, MapPin, User } from "lucide-react";
import { calendarOptions } from "@/config/calendarOptions";
import { useSession } from "next-auth/react";
import { Course } from "@/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";

interface SelectedCourse {
  title: string;
  room?: string;
  instructor?: string;
  code?: string;
  description?: string;
  credits?: number;
  semester?: string;
  department?: string;
  course_type?: string;
  startTime?: Date | null;
  endTime?: Date | null;
  backgroundColor?: string;
}

export function Calendar({
  selectedTimetable,
}: {
  selectedTimetable: number | null;
}) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const { data: session, status } = useSession();
  const [selectedCourse, setSelectedCourse] = useState<SelectedCourse | null>(
    null
  );

  useEffect(() => {
    if (status !== "authenticated" || selectedTimetable === null) {
      setCourses([]);
      return;
    }

    // Fetch the timetable data for the selected timetable
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/timetable/${selectedTimetable}`, {
      headers: {
        Authorization: `Bearer ${session!.user.accessToken}`,
      },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data) => {
        setCourses(data.timetable.courses || []);
      })
      .catch((err) => {
        console.error("Failed to load courses:", err);
        setCourses([]);
      });
  }, [selectedTimetable, status, session]);

  // Only remap courses to events when they change
  const events: EventInput[] = useMemo(() => {
    return courses.map((c) => ({
      id: String(c.id),
      title: c.name,
      daysOfWeek: [c.day_of_week + 1],
      startTime: c.start_time,
      endTime: c.end_time,
      backgroundColor: c.color,
      extendedProps: {
        room: c.room,
        instructor: c.instructor,
        code: c.code,
        description: c.description,
        credits: c.credits,
        course_type: c.course_type,
      },
    }));
  }, [courses]);

  // Handle event click to open dialog with course details
  const handleEventClick = (clickInfo: EventClickArg) => {
    setSelectedCourse({
      title: clickInfo.event.title,
      room: clickInfo.event.extendedProps.room,
      instructor: clickInfo.event.extendedProps.instructor,
      code: clickInfo.event.extendedProps.code,
      description: clickInfo.event.extendedProps.description,
      credits: clickInfo.event.extendedProps.credits,
      semester: clickInfo.event.extendedProps.semester,
      department: clickInfo.event.extendedProps.department,
      course_type: clickInfo.event.extendedProps.course_type,
      startTime: clickInfo.event.start,
      endTime: clickInfo.event.end,
      backgroundColor: clickInfo.event.backgroundColor,
    });
    setDialogOpen(true);
  };

  return (
    <div className="overflow-auto">
      <FullCalendar
        {...calendarOptions}
        initialView="timeGridWeek"
        eventClick={handleEventClick}
        events={events}
        eventContent={renderContent}
      />
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent
          onOpenAutoFocus={(e) => e.preventDefault()}
          className="max-w-md"
        >
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{
                  backgroundColor: selectedCourse?.backgroundColor || "#3b82f6",
                }}
              />
              Kurs Details
            </DialogTitle>
            <DialogDescription>Informationen zu diesem Kurs</DialogDescription>
          </DialogHeader>

          {selectedCourse && (
            <div className="space-y-4 py-4">
              {/* Course Name */}
              <div className="flex items-start gap-3">
                <BookOpen className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-500">Kursname</p>
                  <p className="font-semibold">{selectedCourse.title}</p>
                </div>
              </div>

              {/* Course Code */}
              {selectedCourse.code && (
                <div className="flex items-start gap-3">
                  <CalendarIcon className="w-5 h-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Kurscode
                    </p>
                    <p className="font-medium">{selectedCourse.code}</p>
                  </div>
                </div>
              )}

              {/* Instructor */}
              {selectedCourse.instructor && (
                <div className="flex items-start gap-3">
                  <User className="w-5 h-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Dozent</p>
                    <p className="font-medium">{selectedCourse.instructor}</p>
                  </div>
                </div>
              )}

              {/* Room */}
              {selectedCourse.room && (
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Raum</p>
                    <p className="font-medium">{selectedCourse.room}</p>
                  </div>
                </div>
              )}

              {/* Time */}
              <div className="flex items-start gap-3">
                <Clock className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-500">Zeit</p>
                  <p className="font-medium">
                    {selectedCourse.startTime && selectedCourse.endTime
                      ? `${selectedCourse.startTime.toLocaleTimeString(
                          "de-DE",
                          {
                            hour: "2-digit",
                            minute: "2-digit",
                          }
                        )} - ${selectedCourse.endTime.toLocaleTimeString(
                          "de-DE",
                          {
                            hour: "2-digit",
                            minute: "2-digit",
                          }
                        )}`
                      : "Nicht verfügbar"}
                  </p>
                </div>
              </div>

              {/* Credits */}
              {selectedCourse.credits && (
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-xs font-bold text-blue-600">C</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Credits</p>
                    <p className="font-medium">{selectedCourse.credits}</p>
                  </div>
                </div>
              )}

              {/* Course Type */}
              {selectedCourse.course_type && (
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-xs font-bold text-green-600">T</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Kurstyp</p>
                    <p className="font-medium">{selectedCourse.course_type}</p>
                  </div>
                </div>
              )}

              {/* Department */}
              {selectedCourse.department && (
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-purple-100 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-xs font-bold text-purple-600">D</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Fachbereich
                    </p>
                    <p className="font-medium">{selectedCourse.department}</p>
                  </div>
                </div>
              )}

              {/* Semester */}
              {selectedCourse.semester && (
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-orange-100 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-xs font-bold text-orange-600">S</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Semester
                    </p>
                    <p className="font-medium">{selectedCourse.semester}</p>
                  </div>
                </div>
              )}

              {/* Description */}
              {selectedCourse.description && (
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-gray-100 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-xs font-bold text-gray-600">i</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Beschreibung
                    </p>
                    <p className="font-medium text-sm leading-relaxed">
                      {selectedCourse.description}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function renderContent(info: EventContentArg) {
  return (
    <>
      <div className="relative flex h-full gap-2 overflow-hidden">
        <span className="bg-primary-foreground m-[1px] block h-[calc(100%-2px)] w-[2px] rounded-full"></span>
        <div className="flex flex-col text-xs">
          <div>
            {info.event.extendedProps.room} |{" "}
            {info.event.extendedProps.instructor}
          </div>
          <span className="font-semibold">
            {info.event.title}, {info.event.extendedProps.code}
          </span>
          <span className="flex items-center gap-1">
            <Clock size={11} /> {info.timeText}
          </span>
        </div>
      </div>
    </>
  );
}
