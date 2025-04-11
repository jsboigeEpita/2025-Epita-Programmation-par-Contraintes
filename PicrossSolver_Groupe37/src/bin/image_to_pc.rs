use clap::Parser;
use image::DynamicImage;
use image::GenericImageView;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::vec;

const THRESHOLD: u8 = 128;

#[derive(Parser)]
struct Args {
    image: PathBuf,
    dimension: u32,
}

fn main() -> anyhow::Result<()> {
    let args: Args = Args::parse();

    let mut img: DynamicImage = image::open(&args.image).expect("Failed to open image");

    if img.width() != img.height() {
        panic!("The provided image should be a square image!");
    }

    // Crop image if not multiple of dimension
    let new_size = img.width() - (img.width() % args.dimension);
    img = img.crop(0, 0, new_size, new_size);

    let blocks: Vec<Vec<bool>> = create_blocks(&img, &args.dimension);

    // Open and write to files
    let image_file: String = args
        .image
        .file_stem()
        .expect("Path cannot be empty")
        .to_str()
        .unwrap()
        .to_owned();
    write_blocks_to_file(&blocks, &image_file, &args.dimension);
    write_solutions(&blocks, &image_file, &args.dimension);
    Ok(())
}

fn create_blocks(img: &DynamicImage, dimension: &u32) -> Vec<Vec<bool>> {
    let block_size: u32 = img.width() / *dimension;
    let mut blocks: Vec<Vec<bool>> = vec![vec![false; *dimension as usize]; *dimension as usize];

    for i in (0..img.width()).step_by(block_size as usize) {
        for j in (0..img.height()).step_by(block_size as usize) {
            let mut avg: f64 = 0.0;

            for x in i..i + block_size {
                for y in j..j + block_size {
                    let pixel = img.get_pixel(x, y);
                    let pixel_average =
                        (pixel.0[0] as f64 + pixel.0[1] as f64 + pixel.0[2] as f64) / 3.0;
                    if pixel_average < THRESHOLD as f64 {
                        avg += 1.0;
                    }
                }
            }

            avg /= block_size.pow(2) as f64;
            avg = avg.round();

            let color: u8 = if avg == 1.0 { 255 } else { 0 };
            blocks[(i / block_size) as usize][(j / block_size) as usize] = color == 255;

            for _ in i..i + block_size {
                for _ in j..j + block_size {
                    img.get_pixel(i, j).0 = [color, color, color, 255];
                }
            }
        }
    }
    blocks
}

fn write_blocks_to_file(blocks: &[Vec<bool>], filename: &String, dimension: &u32) {
    let full_filename = format!("{}.pc", filename);
    let mut file = File::create(&full_filename).expect("Failed to create file");

    let mut column_line = String::new();
    let mut row_line = String::new();

    for i in 0..*dimension {
        let row = blocks[i as usize].iter().collect::<Vec<&bool>>();
        let column = blocks.iter().map(|x| x[i as usize]).collect::<Vec<bool>>();

        let mut row_number = 0;
        let mut column_number = 0;

        for j in 0..*dimension {
            // Append row line
            if *row[j as usize] {
                row_number += 1;
            } else if row_number != 0 {
                row_line.push_str(&format!("{} ", row_number));
                row_number = 0;
            }

            // Append column line
            if column[j as usize] {
                column_number += 1;
            } else if column_number != 0 {
                column_line.push_str(&format!("{} ", column_number));
                column_number = 0;
            }
        }
        if column_number != 0 {
            column_line.push_str(&format!("{} ", column_number));
        }
        if row_number != 0 {
            row_line.push_str(&format!("{} ", row_number));
        }

        if i != dimension - 1 {
            column_line.push_str("| ");
            row_line.push_str("| ");
        }
    }
    let full_line = format!("{}\n{}\n", row_line, column_line);
    file.write_all(full_line.as_bytes())
        .expect("Failed to write to file.");
    eprintln!("wrote puzzle to {}", full_filename);
}

fn write_solutions(blocks: &[Vec<bool>], filename: &String, dimension: &u32) {
    let filepath = format!("{}.pcs", filename);
    let mut file = File::create(&filepath).expect("Failed to create file");
    for i in 0..*dimension {
        for j in 0..*dimension {
            let ch = if blocks[j as usize][i as usize] {
                '#'
            } else {
                '.'
            };
            write!(file, "{}", ch).expect("Failed to write to file");
        }
        writeln!(file).expect("Failed to write newline")
    }
    eprintln!("wrote solutions to {}", filepath);
}
